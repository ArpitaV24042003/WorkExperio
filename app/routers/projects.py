# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.crud.projects import create_project, get_projects
# from app.database import get_db

# router = APIRouter(prefix="/projects", tags=["Projects"])

# @router.post("/")
# def create(name: str, description: str, db: Session = Depends(get_db)):
#     return create_project(db, name, description)

# @router.get("/")
# def list_projects(db: Session = Depends(get_db)):
#     return get_projects(db)


# routers/projects.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, database

router = APIRouter(prefix="/projects", tags=["projects"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ProjectOut)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(
        db, 
        user_id=project.user_id, 
        title=project.title, 
        description=project.description or "", 
        technologies=project.technologies or ""
    )

@router.get("/user/{user_id}", response_model=list[schemas.ProjectOut])
def get_user_projects(user_id: int, db: Session = Depends(get_db)):
    return crud.get_projects_by_user(db, user_id)
