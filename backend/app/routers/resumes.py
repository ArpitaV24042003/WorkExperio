from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

# Corrected imports to be specific
from .. import schemas
from ..database import get_db
from ..crud import resumes as crud_resumes # Import 'resumes' from the 'crud' package

# The URL prefix is handled in main.py, so it's removed from here
router = APIRouter(
    tags=["Resumes"]
)

@router.post("/", response_model=schemas.ResumeOut)
def upload_resume(resume: schemas.ResumeIn, db: Session = Depends(get_db)):
    # Call the function from the specific crud_resumes module
    return crud_resumes.create_resume(db, resume=resume)

@router.get("/user/{user_id}", response_model=List[schemas.ResumeOut])
def get_user_resumes(user_id: int, db: Session = Depends(get_db)):
    # Call the function from the specific crud_resumes module
    return crud_resumes.get_resumes_by_user(db, user_id=user_id)