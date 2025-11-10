# app/routers/resumes.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi import Request
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.mongo import resume_raw, resume_parsed, mongo_db
import tempfile, os
import json
from app.routers.users import get_current_user

# Import your resume parsing function
# You said you uploaded resume_parsing.py earlier; it must expose parse_resume(path) -> dict
from app import resume_parsing

router = APIRouter()


@router.post("/parse")
async def parse_resume_endpoint(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    suffix = os.path.splitext(file.filename)[1].lower()
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, file.filename)
    with open(path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Save raw text/binary to Mongo raw collection
    raw_doc = {
        "filename": file.filename,
        "content_type": file.content_type,
        "uploaded_by": current_user.id,
        "uploaded_at": mongo_db.system_js and None,
    }
    # Ideally you'd extract text; for now save file bytes in GridFS or metadata. We'll save metadata + small stored text if small
    try:
        raw_doc["size"] = len(content)
    except Exception:
        raw_doc["size"] = None

    # insert metadata
    raw_res = resume_raw.insert_one(raw_doc)

    # Call your parsing function (should return dict). Wrap with try/catch
    try:
        parsed = resume_parsing.parse_resume(path)
    except Exception as e:
        # cleanup then return error
        try:
            os.remove(path)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")

    # store parsed output in mongo
    parsed_doc = {
        "raw_id": raw_res.inserted_id,
        "parsed": parsed,
        "user_id": current_user.id,
        "created_at":  mongo_db.command("serverStatus").get("localTime") if hasattr(mongo_db, "command") else None
    }
    parsed_res = resume_parsed.insert_one(parsed_doc)

    # Create Resume record in Postgres and update user parsed pointer & summary
    r = models.Resume(
        user_id=current_user.id,
        file_url=f"/resumes/files/{file.filename}",
        parsed_mongo_id=str(parsed_res.inserted_id)
    )
    db.add(r)

    # create a compact JSON summary (skills & top sections) to store in user.parsed_resume_summary
    summary = {"skills": parsed.get("skills", []) if isinstance(parsed, dict) else [], "sections": {k: parsed.get("sections", {}).get(k) for k in ["Education", "Projects", "Certificates"] if isinstance(parsed, dict) and parsed.get("sections")}}
    current_user.parsed_resume_mongo_id = str(parsed_res.inserted_id)
    current_user.parsed_resume_summary = json.dumps(summary)
    current_user.profile_complete = True  # if parsed, mark profile_complete true by default (you can change)
    db.add(current_user)

    db.commit()

    # cleanup the temp file
    try:
        os.remove(path)
    except Exception:
        pass

    # Return parsed JSON to frontend
    return {
        "parsed": parsed,
        "mongo_id": str(parsed_res.inserted_id),
        "summary": summary,
        "resume_record_id": r.id,
    }
