# crud/teams.py
from sqlalchemy.orm import Session
from app import models
from app.schemas import TeamCreate

def create_team(db: Session, team: TeamCreate):
    db_team = models.Team(name=team.name)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

def get_all_teams(db: Session):
    return db.query(models.Team).all()

def get_team_by_id(db: Session, team_id: int):
    return db.query(models.Team).filter(models.Team.id == team_id).first()
