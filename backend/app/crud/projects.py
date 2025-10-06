from sqlalchemy.orm import Session
from .. import models, schemas

# This function is now corrected to accept the Pydantic schema directly
def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        user_id=project.user_id,
        title=project.title,
        description=project.description,
        technologies=project.technologies
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects_by_user(db: Session, user_id: int):
    return db.query(models.Project).filter(models.Project.user_id == user_id).all()

def get_project_by_id(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

