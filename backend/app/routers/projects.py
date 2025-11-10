# app/routers/projects.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app import models
from fastapi import Request

router = APIRouter()


class CreateProjectSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    domain: str | None = None
    skillLevel: str | None = None
    teammates: list | None = []
    aiPlan: dict | None = None
    teamPending: bool | None = False
    teamPendingUntil: str | None = None  # ISO string
    soloAssigned: bool | None = False


# reuse JWT user dependency by importing the same helper (or duplicate small one)
from app.routers.users import get_current_user  # small circular imports okay if module is loaded after routers import in main

@router.post("/")
def create_project(payload: CreateProjectSchema, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    proj = models.Project(
        title=payload.title or f"{payload.domain or 'Project'} - {current_user.name}",
        description=payload.description or "",
        technologies=",".join(payload.aiPlan.get("technologies", [])) if payload.aiPlan and isinstance(payload.aiPlan.get("technologies", []), list) else "",
        user_id=current_user.id,
        team_pending=bool(payload.teamPending),
        team_pending_until=datetime.fromisoformat(payload.teamPendingUntil) if payload.teamPendingUntil else None,
        solo_assigned=bool(payload.soloAssigned),
        status="team_pending" if payload.teamPending else ("active" if payload.soloAssigned else "draft"),
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return {
        "id": proj.id,
        "title": proj.title,
        "description": proj.description,
        "teamPending": proj.team_pending,
        "teamPendingUntil": proj.team_pending_until.isoformat() if proj.team_pending_until else None,
        "soloAssigned": proj.solo_assigned,
        "status": proj.status
    }


@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    proj = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    # basic permission: only owner or team members may view (for now return if owner)
    if proj.user_id != current_user.id:
        # TODO: allow team members to view
        raise HTTPException(status_code=403, detail="Not permitted")
    return {
        "id": proj.id,
        "title": proj.title,
        "description": proj.description,
        "teamPending": proj.team_pending,
        "teamPendingUntil": proj.team_pending_until.isoformat() if proj.team_pending_until else None,
        "soloAssigned": proj.solo_assigned,
        "status": proj.status
    }
