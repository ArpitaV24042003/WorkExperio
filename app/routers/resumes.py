from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

# Corrected imports
from .. import crud, schemas
from ..database import get_db

# REMOVED prefix
router = APIRouter(
    tags=["Resumes"]
)

@router.post("/", response_model=schemas.ResumeOut)
def upload_resume(resume: schemas.ResumeIn, db: Session = Depends(get_db)):
    # This will create the resume entry in PostgreSQL.
    # The resume_text itself can be processed and saved to MongoDB separately.
    return crud.create_resume(db, resume=resume)

@router.get("/user/{user_id}", response_model=List[schemas.ResumeOut])
def get_user_resumes(user_id: int, db: Session = Depends(get_db)):
    return crud.get_resumes_by_user(db, user_id=user_id)
