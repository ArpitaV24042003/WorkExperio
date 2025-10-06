from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud.projects import create_project, get_projects
from app.database import get_db

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/")
def create(name: str, description: str, db: Session = Depends(get_db)):
    return create_project(db, name, description)

@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    return get_projects(db)
