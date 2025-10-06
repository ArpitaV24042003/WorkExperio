# from fastapi import APIRouter

# router = APIRouter()

# @router.get("/")
# def get_teams():
#     return {"message": "List of teams will go here"}


# routers/teams.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud.teams import create_team, get_teams
from app.database import get_db

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.post("/")
def create_team_endpoint(name: str, db: Session = Depends(get_db)):
    return create_team(db, name)

@router.get("/")
def list_teams(db: Session = Depends(get_db)):
    return get_teams(db)
