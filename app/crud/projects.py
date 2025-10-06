# crud/projects.py
from sqlalchemy.orm import Session
from app import models

def create_project(db: Session, user_id: int, title: str, description: str, technologies: str):
    db_project = models.Project(
        user_id=user_id,
        title=title,
        description=description,
        technologies=technologies
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects_by_user(db: Session, user_id: int):
    return db.query(models.Project).filter(models.Project.user_id == user_id).all()

def get_project_by_id(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()
