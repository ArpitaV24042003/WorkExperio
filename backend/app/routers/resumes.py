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

# Note: Removed the broken local import for 'resume_parsing'

router = APIRouter()


@router.post("/parse")
async def parse_resume_endpoint(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    suffix = os.path.splitext(file.filename)[1].lower()
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, file.filename)
    
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    # Save raw text/binary to Mongo raw collection
    raw_doc = {
        "filename": file.filename,
        "content_type": file.content_type,
        "uploaded_by": current_user.id,
        "uploaded_at": mongo_db.system_js and None,
    }
    
    try:
        raw_doc["size"] = len(content)
    except Exception:
        raw_doc["size"] = None

    # insert metadata
    raw_res = resume_raw.insert_one(raw_doc)

    # --- MODIFIED BLOCK: Call AI Service instead of local function ---
    
    # Get AI Service URL from environment variables
    AI_SERVICE_URL = os.getenv("AI_SERVICE_URL")
    if not AI_SERVICE_URL:
        # This is a server configuration error
        raise HTTPException(status_code=500, detail="AI_SERVICE_URL is not set")

    # Define the endpoint on your AI service
    # IMPORTANT: You must create this endpoint (e.g., /parse-resume) in your ai_service project
    parse_endpoint = f"{AI_SERVICE_URL}/parse-resume"
    
    files_to_send = {'file': (file.filename, content, file.content_type)}
    
    try:
        # Call your external AI service
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(parse_endpoint, files=files_to_send)
            
            # Raise an exception if the AI service returned an error (4xx or 5xx)
            response.raise_for_status() 
            
            # Get the parsed JSON data from the response
            parsed = response.json() 

    except httpx.RequestError as e:
        # Network error, AI service is down or unreachable
        try:
            os.remove(path)
        except Exception:
            pass
        raise HTTPException(status_code=503, detail=f"AI service connection error: {str(e)}")
    except httpx.HTTPStatusError as e:
        # AI service returned a non-200 status code
        try:
            os.remove(path)
        except Exception:
            pass
        raise HTTPException(status_code=e.response.status_code, detail=f"AI service returned error: {e.response.text}")
    except Exception as e:
        # Other unexpected errors (e.g., JSON decode error if AI service response is malformed)
        try:
            os.remove(path)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")
    
    # --- END OF MODIFIED BLOCK ---

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