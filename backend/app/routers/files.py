from pathlib import Path
from typing import List
import os
import zipfile
import shutil
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import get_current_user
from ..models import Project, ProjectFile, Team, TeamMember, UserStats, User
from ..schemas import ProjectFileRead, ProjectFileUploadResponse

router = APIRouter()

# Upload directory for project files
UPLOAD_DIR = Path("backend/uploads/projects")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Maximum file size: 100MB
MAX_FILE_SIZE = 100 * 1024 * 1024


def get_mime_type(filename: str) -> str:
	"""Get MIME type from filename extension"""
	ext = Path(filename).suffix.lower()
	mime_types = {
		# Code files
		".py": "text/x-python",
		".js": "text/javascript",
		".jsx": "text/javascript",
		".ts": "text/typescript",
		".tsx": "text/typescript",
		".html": "text/html",
		".css": "text/css",
		".json": "application/json",
		".md": "text/markdown",
		".txt": "text/plain",
		# Archives
		".zip": "application/zip",
		# Documents
		".pdf": "application/pdf",
		".doc": "application/msword",
		".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
		# Images - for reports and displays
		".jpg": "image/jpeg",
		".jpeg": "image/jpeg",
		".png": "image/png",
		".gif": "image/gif",
		".svg": "image/svg+xml",
		".webp": "image/webp",
		".bmp": "image/bmp",
		".ico": "image/x-icon",
	}
	return mime_types.get(ext, "application/octet-stream")


def get_file_type(filename: str) -> str:
	"""Determine file type category"""
	ext = Path(filename).suffix.lower()
	code_extensions = {".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".json", ".md", ".java", ".cpp", ".c", ".go", ".rs", ".php", ".rb"}
	doc_extensions = {".pdf", ".doc", ".docx", ".txt", ".md"}
	image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".bmp", ".ico"}
	
	if ext in code_extensions:
		return "code"
	elif ext in doc_extensions:
		return "document"
	elif ext in image_extensions:
		return "image"  # For pictures/images in reports
	elif ext == ".zip":
		return "folder"
	else:
		return "other"


@router.post("/projects/{project_id}/upload", response_model=ProjectFileUploadResponse)
async def upload_project_file(
	project_id: str,
	file: UploadFile = File(...),
	description: str = Form(None),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""Upload a file or folder (as zip) for a project"""
	# Verify project exists and user has access
	project = db.query(Project).filter(Project.id == project_id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
	
	# Check if user is owner or team member
	if project.owner_id != current_user.id:
		if project.team_id:
			team = db.query(Team).filter(Team.id == project.team_id).first()
			if team:
				member = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == current_user.id).first()
				if not member:
					raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to upload files to this project")
			else:
				raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to upload files to this project")
		else:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to upload files to this project")
	
	# Read file content
	contents = await file.read()
	file_size = len(contents)
	
	# Check file size
	if file_size > MAX_FILE_SIZE:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB")
	
	# Create project-specific directory
	project_dir = UPLOAD_DIR / project_id
	project_dir.mkdir(parents=True, exist_ok=True)
	
	# Save file
	file_path = project_dir / file.filename
	file_path.write_bytes(contents)
	
	# Determine file type and MIME type
	file_type = get_file_type(file.filename)
	mime_type = get_mime_type(file.filename)
	
	# If it's a zip file, extract it to a folder (optional - you can handle this differently)
	if file_type == "folder" and file.filename.endswith(".zip"):
		# Extract zip to a folder with the same name (without .zip)
		extract_dir = project_dir / Path(file.filename).stem
		with zipfile.ZipFile(file_path, 'r') as zip_ref:
			zip_ref.extractall(extract_dir)
	
	# Create database record
	project_file = ProjectFile(
		project_id=project_id,
		user_id=current_user.id,
		filename=file.filename,
		file_path=str(file_path.relative_to(UPLOAD_DIR)),
		file_size=file_size,
		file_type=file_type,
		mime_type=mime_type,
		description=description,
	)
	db.add(project_file)
	
	# Update user stats - increment files_uploaded metric
	user_stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()
	if user_stats:
		user_stats.files_uploaded = (user_stats.files_uploaded or 0) + 1
	
	db.commit()
	db.refresh(project_file)
	
	return ProjectFileUploadResponse(
		id=project_file.id,
		filename=project_file.filename,
		file_size=project_file.file_size,
		uploaded_at=project_file.uploaded_at,
		message="File uploaded successfully"
	)


@router.get("/projects/{project_id}/files", response_model=List[ProjectFileRead])
def list_project_files(
	project_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""List all files uploaded for a project"""
	# Verify project exists and user has access
	project = db.query(Project).filter(Project.id == project_id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
	
	# Check if user is owner or team member
	if project.owner_id != current_user.id:
		if project.team_id:
			team = db.query(Team).filter(Team.id == project.team_id).first()
			if team:
				member = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == current_user.id).first()
				if not member:
					raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view files for this project")
			else:
				raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view files for this project")
		else:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view files for this project")
	
	# Get all files for the project
	files = db.query(ProjectFile).filter(ProjectFile.project_id == project_id).order_by(ProjectFile.uploaded_at.desc()).all()
	return [ProjectFileRead.model_validate(f) for f in files]


@router.get("/projects/{project_id}/files/{file_id}/download")
def download_project_file(
	project_id: str,
	file_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""Download a project file"""
	# Verify file exists and user has access
	project_file = db.query(ProjectFile).filter(ProjectFile.id == file_id, ProjectFile.project_id == project_id).first()
	if not project_file:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
	
	# Verify project access
	project = db.query(Project).filter(Project.id == project_id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
	
	# Check if user is owner or team member
	if project.owner_id != current_user.id:
		if project.team_id:
			team = db.query(Team).filter(Team.id == project.team_id).first()
			if team:
				member = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == current_user.id).first()
				if not member:
					raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to download files from this project")
			else:
				raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to download files from this project")
		else:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to download files from this project")
	
	# Construct full file path
	file_path = UPLOAD_DIR / project_file.file_path
	
	if not file_path.exists():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk")
	
	return FileResponse(
		path=str(file_path),
		filename=project_file.filename,
		media_type=project_file.mime_type or "application/octet-stream"
	)


@router.delete("/projects/{project_id}/files/{file_id}")
def delete_project_file(
	project_id: str,
	file_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""Delete a project file (only owner or file uploader can delete)"""
	# Verify file exists
	project_file = db.query(ProjectFile).filter(ProjectFile.id == file_id, ProjectFile.project_id == project_id).first()
	if not project_file:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
	
	# Verify project access
	project = db.query(Project).filter(Project.id == project_id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
	
	# Only owner or file uploader can delete
	if project.owner_id != current_user.id and project_file.user_id != current_user.id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this file")
	
	# Delete file from disk
	file_path = UPLOAD_DIR / project_file.file_path
	if file_path.exists():
		if file_path.is_file():
			file_path.unlink()
		elif file_path.is_dir():
			shutil.rmtree(file_path)
	
	# Delete database record
	db.delete(project_file)
	db.commit()
	
	return {"message": "File deleted successfully"}

