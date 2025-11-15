from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import get_current_user
from ..models import Project, Team, TeamMember, ProjectWaitlist, User
from ..ai.team_selection import recommend_team
from ..schemas import (
	TeamSuggestionRequest,
	TeamAssignRequest,
	TeamRead,
	TeamMemberRead,
	WaitlistRequest,
	WaitlistEntryRead,
)

router = APIRouter()

WAITLIST_DURATION = timedelta(days=7)


@router.post("/ml/team-selection")
def team_selection(payload: TeamSuggestionRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	project = db.query(Project).filter(Project.id == payload.project_id, Project.owner_id == current_user.id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

	user_profiles = [profile.model_dump() for profile in payload.candidate_profiles]
	recommendations = recommend_team(user_profiles, payload.required_skills)
	return recommendations


@router.post("/projects/{project_id}/assign-team", response_model=TeamRead)
def assign_team(
	project_id: str,
	payload: TeamAssignRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

	team = Team(project_id=project_id)
	db.add(team)
	db.flush()

	for user_id in payload.user_ids:
		role = payload.role_map.get(user_id) if payload.role_map else None
		db.add(TeamMember(team_id=team.id, user_id=user_id, role=role))

	project.team_id = team.id
	project.team_type = "team"
	db.commit()
	db.refresh(team)
	return team


@router.get("/projects/{project_id}/team", response_model=dict[str, Any])
def get_team(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
	if not project or not project.team_id:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not assigned")
	team = db.query(Team).filter(Team.id == project.team_id).first()
	members = db.query(TeamMember).filter(TeamMember.team_id == team.id).all()
	return {
		"team": TeamRead.model_validate(team),
		"members": [TeamMemberRead.model_validate(member) for member in members],
	}


@router.post("/projects/{project_id}/waitlist", response_model=WaitlistEntryRead)
def join_waitlist(
	project_id: str,
	payload: WaitlistRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

	entry = ProjectWaitlist(project_id=project_id, user_id=payload.user_id)
	db.add(entry)
	project.team_type = "none"
	db.commit()
	db.refresh(entry)
	return entry


@router.get("/projects/{project_id}/waitlist-status")
def waitlist_status(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

	entries = db.query(ProjectWaitlist).filter(ProjectWaitlist.project_id == project_id).all()
	now = datetime.now(timezone.utc)
	status_entries = []
	for entry in entries:
		elapsed = now - entry.created_at.replace(tzinfo=timezone.utc)
		days_left = max(0, (WAITLIST_DURATION - elapsed).days)
		status_entries.append(
			{
				"id": entry.id,
				"user_id": entry.user_id,
				"created_at": entry.created_at,
				"days_left": days_left,
			}
		)

	return {
		"project_id": project_id,
		"entries": status_entries,
		"auto_solo_at": entries[0].created_at + WAITLIST_DURATION if entries else None,
	}
# app/routers/teams.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from .. import schemas
from ..db import get_db
from ..crud import teams as crud_teams
from .. import models

router = APIRouter()

# --- Local Pydantic models (move to schemas.py if you prefer) ---
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
    required_skill_ids: List[int] = []

class RoleOut(BaseModel):
    id: int
    name: str
    domain_id: int
    class Config:
        orm_mode = True

class TeamProjectCreate(BaseModel):
    project_name: str
    description: str
    project_plan_json: Optional[str] = None

class TeamProjectOut(TeamProjectCreate):
    id: int
    team_id: int
    status: str
    class Config:
        orm_mode = True

# --- Team endpoints ---
@router.post("/", response_model=schemas.TeamOut)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    """
    Create a new team. Also creates a ChatRoom for the team.
    """
    db_team = crud_teams.create_team(db, team)

    # create associated chat room (if ChatRoom model exists)
    try:
        new_chat_room = models.ChatRoom(name=f"{db_team.name} Room", team_id=db_team.id)
        db.add(new_chat_room)
        db.commit()
    except Exception:
        # optional: log exception in real app
        db.rollback()

    db.refresh(db_team)
    return db_team

@router.get("/", response_model=List[schemas.TeamOut])
def list_teams(db: Session = Depends(get_db)):
    return crud_teams.get_all_teams(db)

# --- Domains endpoints ---
@router.post("/domains", response_model=DomainOut)
def create_domain(domain: DomainCreate, db: Session = Depends(get_db)):
    db_domain = models.Domain(**domain.dict())
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain

@router.get("/domains", response_model=List[DomainOut])
def list_domains(db: Session = Depends(get_db)):
    return db.query(models.Domain).all()

# --- Roles endpoints ---
@router.post("/roles", response_model=RoleOut)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    domain = db.query(models.Domain).filter(models.Domain.id == role.domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    skills = db.query(models.Skill).filter(models.Skill.id.in_(role.required_skill_ids)).all()
    if len(skills) != len(role.required_skill_ids):
        raise HTTPException(status_code=404, detail="One or more skills not found")

    db_role = models.Role(name=role.name, domain_id=role.domain_id)
    # link many-to-many if relationship defined
    if hasattr(db_role, "required_skills"):
        db_role.required_skills.extend(skills)

    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@router.get("/roles", response_model=List[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    return db.query(models.Role).all()

# --- Team Project endpoints (team-scoped projects) ---
@router.post("/teams/{team_id}/projects", response_model=TeamProjectOut)
def create_team_project(team_id: int, project: TeamProjectCreate, db: Session = Depends(get_db)):
    db_team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    db_project = models.TeamProject(**project.dict(), team_id=team_id, status="planning")
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
