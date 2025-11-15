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
