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


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import schemas
from ..database import get_db
from ..crud import projects as crud_projects

router = APIRouter(tags=["Projects"])

@router.post("/", response_model=schemas.ProjectOut)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud_projects.create_project(db=db, project=project)

@router.get("/user/{user_id}", response_model=List[schemas.ProjectOut])
def get_user_projects(user_id: int, db: Session = Depends(get_db)):
    return crud_projects.get_projects_by_user(db, user_id=user_id)
