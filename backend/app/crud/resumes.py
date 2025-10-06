# crud/resumes.py
from sqlalchemy.orm import Session
from app import models
from app.schemas import ResumeIn

def create_resume(db: Session, resume: ResumeIn, parsed_mongo_id: str = None, is_verified: bool = False):
    db_resume = models.Resume(
        user_id=resume.user_id,
        file_url=resume.file_url,
        parsed_mongo_id=parsed_mongo_id,
        manual_additions=resume.resume_text,
        is_verified=is_verified
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def get_resumes_by_user(db: Session, user_id: int):
    return db.query(models.Resume).filter(models.Resume.user_id == user_id).all()

def get_resume_by_id(db: Session, resume_id: int):
    return db.query(models.Resume).filter(models.Resume.id == resume_id).first()

def update_resume_verification(db: Session, resume_id: int, verified: bool):
    resume = get_resume_by_id(db, resume_id)
    if resume:
        resume.is_verified = verified
        db.commit()
        db.refresh(resume)
    return resume
