from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..db import get_db
from ..dependencies import get_current_user
from ..models import Project, ModelPrediction
from ..schemas import ProjectCreate, ProjectRead
from ..ai.project_generator import generate_project_idea
from ..ai.team_selection import recommend_team
from ..models import User, Skill

router = APIRouter()


@router.post("", response_model=ProjectRead)
def create_project(
	payload: ProjectCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	project = Project(
		title=payload.title,
		description=payload.description,
		owner_id=current_user.id,
		team_type=payload.team_type,
		ai_generated=payload.ai_generated,
	)
	db.add(project)
	db.commit()
	db.refresh(project)
	return project


@router.get("", response_model=list[ProjectRead])
def list_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	return db.query(Project).filter(Project.owner_id == current_user.id).order_by(Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
	return project


@router.post("/ai-generate", response_model=Dict[str, Any])
def ai_generate_project(
	payload: Dict[str, Any],
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""
	Generate project idea based on skills. 
	If team members are provided, combines all their skills.
	"""
	# Get current user's skills
	current_user_skills = [skill.name for skill in db.query(Skill).filter(Skill.user_id == current_user.id)]
	
	# Get team member skills if provided
	team_member_ids = payload.get("candidate_profiles", [])
	all_skills = set(current_user_skills)
	
	# Fetch skills from team members
	for member_profile in team_member_ids:
		member_id = member_profile.get("user_id") if isinstance(member_profile, dict) else member_profile
		if isinstance(member_id, str):
			member_skills = [skill.name for skill in db.query(Skill).filter(Skill.user_id == member_id)]
			all_skills.update(member_skills)
		elif isinstance(member_profile, dict) and "skills" in member_profile:
			# Skills already provided in profile
			all_skills.update(member_profile["skills"])
	
	# Use provided skills or combined team skills
	skills = payload.get("skills") or list(all_skills)
	experience_level = payload.get("experience_level", "intermediate")
	
	# Determine experience level based on team
	if team_member_ids:
		# If team has members, consider it intermediate/advanced
		experience_level = "intermediate"
	
	idea = generate_project_idea(skills, experience_level)
	model_log = ModelPrediction(
		project_id=None,
		model_name="project_generator",
		input_json={"skills": skills, "experience_level": experience_level, "team_size": len(team_member_ids) + 1},
		output_json=idea,
		score=None,
	)
	db.add(model_log)
	db.commit()
	return idea


@router.post("/ai-generate-project", response_model=Dict[str, Any])
def ai_generate_project_with_team(
	payload: Dict[str, Any],
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	idea = ai_generate_project(payload, current_user, db)
	project_requirements = payload.get("project_requirements", payload.get("skills", []))
	user_profiles = payload.get("candidate_profiles", [])
	recommendations = recommend_team(user_profiles, project_requirements)
	return {
		"project": idea,
		"team_recommendation": recommendations,
	}
