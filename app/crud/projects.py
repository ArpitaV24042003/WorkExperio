from sqlalchemy.orm import Session
from app import models

def create_project(db: Session, name: str, description: str):
    project = models.Project(name=name, description=description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def get_projects(db: Session):
    return db.query(models.Project).all()
