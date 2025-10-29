# crud/team_projects.py
from sqlalchemy.orm import Session
from .. import models, schemas
from fastapi import HTTPException

def create_team_project(db: Session, team_id: int, project: schemas.TeamProjectCreate):
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    db_project = models.TeamProject(
        **project.dict(), 
        team_id=team_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects_for_team(db: Session, team_id: int):
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return db.query(models.TeamProject).filter(models.TeamProject.team_id == team_id).all()