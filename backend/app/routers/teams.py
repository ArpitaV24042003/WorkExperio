# # # from fastapi import APIRouter

# # # router = APIRouter()

# # # @router.get("/")
# # # def get_teams():
# # #     return {"message": "List of teams will go here"}


# # # routers/teams.py
# # from fastapi import APIRouter, Depends
# # from sqlalchemy.orm import Session
# # from app.crud.teams import create_team, get_teams
# # from app.database import get_db

# # router = APIRouter(prefix="/teams", tags=["Teams"])

# # @router.post("/")
# # def create_team_endpoint(name: str, db: Session = Depends(get_db)):
# #     return create_team(db, name)

# # @router.get("/")
# # def list_teams(db: Session = Depends(get_db)):
# #     return get_teams(db)


# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from typing import List
# from .. import schemas
# from ..database import get_db
# from ..crud import teams as crud_teams

# router = APIRouter(tags=["Teams"])

# @router.post("/", response_model=schemas.TeamOut)
# def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
#     return crud_teams.create_team(db, team)

# @router.get("/", response_model=List[schemas.TeamOut])
# def list_teams(db: Session = Depends(get_db)):
#     return crud_teams.get_all_teams(db)


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from pydantic import BaseModel
from .. import schemas
from ..database import get_db
from ..crud import teams as crud_teams
from .. import models # NEW: Import models

router = APIRouter(tags=["Teams"])

# --- NEW SCHEMAS ---
# (You should move these to schemas.py)

class DomainCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DomainOut(DomainCreate):
    id: int
    class Config:
        orm_mode = True

class RoleCreate(BaseModel):
    name: str
    domain_id: int
    required_skill_ids: List[int] = [] # List of Skill IDs

class RoleOut(BaseModel):
    id: int
    name: str
    domain_id: int
    class Config:
        orm_mode = True

class TeamProjectCreate(BaseModel):
    project_name: str
    description: str
    project_plan_json: Optional[str] = None # This will hold the JSON from team_ps_selection.py

class TeamProjectOut(TeamProjectCreate):
    id: int
    team_id: int
    status: str
    class Config:
        orm_mode = True

#
# --- TEAM ENDPOINTS (MODIFIED) ---
#
@router.post("/", response_model=schemas.TeamOut)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    """
    Create a new team. This will also automatically create 
    a dedicated ChatRoom for this team.
    """
    # Use your existing CRUD function to create the team
    db_team = crud_teams.create_team(db, team)
    
    # NEW: Create the associated chat room
    new_chat_room = models.ChatRoom(
        name=f"{db_team.name} Room",
        team_id=db_team.id
    )
    db.add(new_chat_room)
    db.commit()
    db.refresh(db_team) # Refresh to get the room relationship
    
    return db_team

@router.get("/", response_model=List[schemas.TeamOut])
def list_teams(db: Session = Depends(get_db)):
    return crud_teams.get_all_teams(db)

#
# --- NEW: DOMAIN ENDPOINTS (for team_formation.py config) ---
#
@router.post("/domains", response_model=DomainOut)
def create_domain(domain: DomainCreate, db: Session = Depends(get_db)):
    """
    Create a new project domain (e.g., "Frontend Development").
    """
    db_domain = models.Domain(**domain.dict())
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain

@router.get("/domains", response_model=List[DomainOut])
def list_domains(db: Session = Depends(get_db)):
    return db.query(models.Domain).all()

#
# --- NEW: ROLE ENDPOINTS (for team_formation.py config) ---
#
@router.post("/roles", response_model=RoleOut)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    """
    Create a new role and link it to required skills.
    """
    # Check if domain exists
    domain = db.query(models.Domain).filter(models.Domain.id == role.domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
        
    # Check if skills exist and fetch them
    skills = db.query(models.Skill).filter(models.Skill.id.in_(role.required_skill_ids)).all()
    if len(skills) != len(role.required_skill_ids):
        raise HTTPException(status_code=404, detail="One or more skills not found")

    db_role = models.Role(name=role.name, domain_id=role.domain_id)
    db_role.required_skills.extend(skills) # Add the skill relationships
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@router.get("/roles", response_model=List[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    return db.query(models.Role).all()

#
# --- NEW: TEAM PROJECT ENDPOINTS (for team_ps_selection.py output) ---
#
@router.post("/teams/{team_id}/projects", response_model=TeamProjectOut)
def create_team_project(
    team_id: int, 
    project: TeamProjectCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new project for a team and store its plan.
    """
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    db_project = models.TeamProject(**project.dict(), team_id=team_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/teams/{team_id}/projects", response_model=List[TeamProjectOut])
def get_team_projects(team_id: int, db: Session = Depends(get_db)):
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return db.query(models.TeamProject).filter(models.TeamProject.team_id == team_id).all()