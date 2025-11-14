from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Resume, User
from ..schemas import ResumeRead, ResumeUploadResponse
from ..dependencies import get_current_user
from ..ai.resume_parser import parse_pdf_resume

router = APIRouter()

UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/parse", response_model=ResumeUploadResponse)
async def parse_resume(
	file: UploadFile = File(...),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	if not file.filename:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file upload")

	contents = await file.read()
	parsed = parse_pdf_resume(contents, file.filename)

	file_path = UPLOAD_DIR / file.filename
	file_path.write_bytes(contents)

	resume = Resume(user_id=current_user.id, filename=file.filename, parsed_json=parsed)
	db.add(resume)
	db.commit()
	db.refresh(resume)

	return ResumeUploadResponse(id=resume.id, filename=resume.filename, uploaded_at=resume.uploaded_at)


@router.get("/{resume_id}", response_model=ResumeRead)
def get_resume(
	resume_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	resume: Optional[Resume] = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
	if not resume:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
	return resume
# backend/app/routers/resumes.py
import os
import tempfile
import json
import datetime
from typing import Optional

import httpx
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.mongo import resume_raw, resume_parsed, mongo_db
from app.routers.users import get_current_user  # existing dependency to get current user

router = APIRouter()


@router.post("/parse")
async def parse_resume_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Upload a resume file, send it to an external AI parsing service, store raw + parsed into MongoDB and
    create a Resume row in Postgres (and update the user's parsed_resume_summary).
    """

    # Basic validation
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Read file bytes once
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {str(e)}")

    # Temp save (optional, used for debugging / compatibility)
    tmpdir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmpdir, file.filename)
    try:
        with open(tmp_path, "wb") as f:
            f.write(content)
    except Exception:
        # non-fatal; continue without temp file if we couldn't write
        tmp_path = None

    # Prepare raw doc metadata for Mongo
    now = datetime.datetime.utcnow()
    raw_doc = {
        "filename": file.filename,
        "content_type": file.content_type,
        "uploaded_by": getattr(current_user, "id", None),
        "uploaded_at": now,
    }
    try:
        raw_doc["size"] = len(content)
    except Exception:
        raw_doc["size"] = None

    # Insert raw metadata
    try:
        raw_res = resume_raw.insert_one(raw_doc)
    except Exception as e:
        # Cleanup temp file
        if tmp_path:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to save raw resume metadata: {str(e)}")

    # --- Call external AI service to parse resume ---
    AI_SERVICE_URL = os.getenv("AI_SERVICE_URL")  # e.g. https://ai-service.example.com
    if not AI_SERVICE_URL:
        # If you would prefer local fallback, implement it here.
        # For now, signal a server-side misconfiguration so frontend shows a proper error.
        raise HTTPException(status_code=503, detail="AI_SERVICE_URL is not configured on the server")

    # Try a couple of plausible endpoints so the backend will work whether AI exposes /parse-resume or /ai/resume-parse
    candidate_paths = ["/parse-resume", "/ai/resume-parse", "/resume/parse", "/ai/parse-resume"]
    parsed = None
    last_exc: Optional[Exception] = None

    # Build the files payload for httpx: ('filename', bytes, content_type)
    files_to_send = {"file": (file.filename, content, file.content_type or "application/octet-stream")}

    async with httpx.AsyncClient(timeout=60.0) as client:
        for p in candidate_paths:
            url = AI_SERVICE_URL.rstrip("/") + p
            try:
                resp = await client.post(url, files=files_to_send)
                # if AI service uses /ai prefix with other base, it might return 404; try next candidate
                if resp.status_code == 404:
                    continue
                resp.raise_for_status()
                # Attempt to parse response JSON
                try:
                    parsed = resp.json()
                except Exception:
                    # if response isn't JSON, raise
                    raise HTTPException(status_code=502, detail=f"AI service returned non-JSON at {url}")
                # success -> break
                break
            except httpx.RequestError as rex:
                last_exc = rex
                # network error: try next endpoint candidate
                continue
            except httpx.HTTPStatusError as hexc:
                # If AI service returned non-2xx other than 404, stop and bubble up
                last_exc = hexc
                # prefer to pass detailed message
                detail = f"AI service at {url} returned {hexc.response.status_code}: {hexc.response.text}"
                raise HTTPException(status_code=502, detail=detail)
        else:
            # exhausted candidates
            if last_exc:
                raise HTTPException(status_code=503, detail=f"Could not reach AI service: {str(last_exc)}")
            raise HTTPException(status_code=502, detail="AI service did not return parsed data")

    # --- Persist parsed output to Mongo ---
    parsed_doc = {
        "raw_id": getattr(raw_res, "inserted_id", None),
        "parsed": parsed,
        "user_id": getattr(current_user, "id", None),
        "created_at": now,
    }
    try:
        parsed_res = resume_parsed.insert_one(parsed_doc)
    except Exception as e:
        # Cleanup temp file
        if tmp_path:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to save parsed resume: {str(e)}")

    # --- Create Postgres Resume record and update user summary ---
    try:
        r = models.Resume(
            user_id=current_user.id,
            file_url=f"/resumes/files/{file.filename}",
            parsed_mongo_id=str(parsed_res.inserted_id),
        )
        db.add(r)

        # Build compact summary: best-effort extraction of skills & sections
        summary = {
            "skills": parsed.get("skills", []) if isinstance(parsed, dict) else [],
            "sections": {},
        }
        if isinstance(parsed, dict):
            sections = parsed.get("sections", {})
            if isinstance(sections, dict):
                for k in ("Education", "Projects", "Certificates", "Experience"):
                    if sections.get(k):
                        summary["sections"][k] = sections.get(k)

        # update user fields (non-destructive)
        current_user.parsed_resume_mongo_id = str(parsed_res.inserted_id)
        try:
            current_user.parsed_resume_summary = json.dumps(summary)
        except Exception:
            current_user.parsed_resume_summary = None

        # Optionally mark profile_complete true if parsing succeeded
        current_user.profile_complete = True

        db.add(current_user)
        db.commit()
        db.refresh(r)
    except Exception as e:
        # If DB commit fails, we should at least return parsed output; but signal failure to create Resume record
        # (Don't swallow the error entirely)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create resume record or update user: {str(e)}")
    finally:
        # cleanup tmp file
        if tmp_path:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    # --- Return parsed payload to frontend ---
    return {
        "parsed": parsed,
        "mongo_raw_id": str(raw_res.inserted_id) if getattr(raw_res, "inserted_id", None) else None,
        "mongo_parsed_id": str(parsed_res.inserted_id) if getattr(parsed_res, "inserted_id", None) else None,
        "summary": summary,
        "resume_record_id": getattr(r, "id", None),
    }
