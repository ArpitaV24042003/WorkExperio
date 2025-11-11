# app/routers/resumes.py
import httpx
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi import Request
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.mongo import resume_raw, resume_parsed, mongo_db
import tempfile
import os
import json
from app.routers.users import get_current_user
from datetime import datetime
import traceback

router = APIRouter()

@router.post("/parse")
async def parse_resume_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Upload resume, forward to AI service (if configured) or local parser (if available),
    persist raw + parsed to Mongo and record a Resume entry in Postgres.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, file.filename)

    try:
        content = await file.read()
        with open(path, "wb") as f:
            f.write(content)
    except Exception as e:
        # cleanup and return error
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    # Save raw metadata to Mongo (non-blocking-ish)
    raw_doc = {
        "filename": file.filename,
        "content_type": file.content_type,
        "uploaded_by": current_user.id if current_user is not None else None,
        # uploaded_at: prefer Mongo server time if available, else use UTC now
        "uploaded_at": None,
    }

    try:
        # If mongo_db has serverStatus, attempt to fetch server local time.
        server_time = None
        try:
            ss = mongo_db.command("serverStatus")
            server_time = ss.get("localTime")
        except Exception:
            server_time = None

        raw_doc["uploaded_at"] = server_time if server_time is not None else datetime.utcnow()
        raw_doc["size"] = len(content)
    except Exception:
        # fallback metadata
        raw_doc["size"] = None

    raw_res = None
    try:
        raw_res = resume_raw.insert_one(raw_doc)
    except Exception as e:
        # Log insertion failure but continue — we still want to try parsing
        print("Warning: failed to write resume raw metadata to mongo:", str(e))

    # --- AI parsing logic ---
    AI_SERVICE_URL = os.getenv("AI_SERVICE_URL")
    parsed = None

    # Helper to cleanup temp file
    def _cleanup_tmp():
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
        try:
            if os.path.isdir(tmpdir):
                os.rmdir(tmpdir)
        except Exception:
            pass

    # 1) If AI_SERVICE_URL configured, call it
    if AI_SERVICE_URL:
        parse_endpoint = AI_SERVICE_URL.rstrip("/") + "/parse-resume"
        files_to_send = {"file": (file.filename, content, file.content_type)}
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(parse_endpoint, files=files_to_send)
                resp.raise_for_status()
                parsed = resp.json()
        except httpx.RequestError as e:
            _cleanup_tmp()
            raise HTTPException(status_code=503, detail=f"AI service connection error: {str(e)}")
        except httpx.HTTPStatusError as e:
            _cleanup_tmp()
            raise HTTPException(status_code=e.response.status_code, detail=f"AI service returned error: {e.response.text}")
        except Exception as e:
            _cleanup_tmp()
            raise HTTPException(status_code=500, detail=f"AI service parsing failed: {str(e)}")
    else:
        # 2) Try to use a local parser module if present (ai_service.ai_model.resume_parsing)
        try:
            local_mod = __import__("ai_service.ai_model.resume_parsing", fromlist=["parse_bytes"])
            parse_fn = getattr(local_mod, "parse_bytes", None) or getattr(local_mod, "parse_resume_bytes", None)
            if parse_fn:
                try:
                    parsed = parse_fn(content)  # support sync function
                    # if coroutine returned, await it
                    if hasattr(parsed, "__await__"):
                        parsed = await parsed
                except Exception as e:
                    _cleanup_tmp()
                    raise HTTPException(status_code=500, detail=f"Local parser failed: {str(e)}")
            else:
                # No parser available
                _cleanup_tmp()
                raise HTTPException(status_code=503, detail="No AI_SERVICE_URL configured and no local parser available")
        except ModuleNotFoundError:
            _cleanup_tmp()
            raise HTTPException(status_code=503, detail="AI service not configured and no local parser available")
        except Exception as e:
            _cleanup_tmp()
            raise HTTPException(status_code=500, detail=f"Unexpected error loading local parser: {str(e)}")

    # store parsed output in mongo
    try:
        parsed_doc = {
            "raw_id": str(raw_res.inserted_id) if raw_res else None,
            "parsed": parsed,
            "user_id": current_user.id if current_user is not None else None,
            "created_at": datetime.utcnow(),
        }
        parsed_res = resume_parsed.insert_one(parsed_doc)
    except Exception as e:
        # cleanup temp file and bubble an error
        _cleanup_tmp()
        print("Error saving parsed resume to mongo:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to store parsed resume: {str(e)}")

    # Create Resume record in Postgres and update user parsed pointer & summary
    try:
        r = models.Resume(
            user_id=current_user.id,
            file_url=f"/resumes/files/{file.filename}",
            parsed_mongo_id=str(parsed_res.inserted_id),
        )
        db.add(r)

        # create a compact JSON summary (skills & top sections) to store in user.parsed_resume_summary
        summary = {
            "skills": parsed.get("skills", []) if isinstance(parsed, dict) else [],
            "sections": {
                k: parsed.get("sections", {}).get(k)
                for k in ["Education", "Projects", "Certificates"]
                if isinstance(parsed, dict) and parsed.get("sections")
            },
        }

        current_user.parsed_resume_mongo_id = str(parsed_res.inserted_id)
        current_user.parsed_resume_summary = json.dumps(summary)
        current_user.profile_complete = True  # if parsed, mark profile_complete true by default
        db.add(current_user)
        db.commit()
    except Exception as e:
        db.rollback()
        _cleanup_tmp()
        print("Error saving Resume record / updating user:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to save resume record: {str(e)}")

    # cleanup the temp file and directory
    _cleanup_tmp()

    # Return parsed JSON to frontend
    return {
        "parsed": parsed,
        "mongo_id": str(parsed_res.inserted_id),
        "summary": summary,
        "resume_record_id": r.id,
    }
