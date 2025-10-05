from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.mongo import resume_raw
import httpx, os

router = APIRouter()
ML_BASE = os.getenv("ML_BASE_URL", "http://localhost:8001")

@router.post("/")
async def upload_resume(payload: dict, db: Session = Depends(get_db)):
    user_id = payload.get("user_id")
    resume_text = payload.get("resume_text")
    if not user_id or not resume_text:
        raise HTTPException(400, "user_id and resume_text required")

    # store raw in Mongo
    resume_raw.insert_one({"user_id": user_id, "text": resume_text})

    # call ML service
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{ML_BASE}/parse", json={"text": resume_text})
        parsed = resp.json()

    # save in Postgres
    resume = models.Resume(user_id=user_id, skills=parsed.get("skills"))
    db.add(resume); db.commit(); db.refresh(resume)

    return {"message": "Resume processed", "parsed": parsed}
