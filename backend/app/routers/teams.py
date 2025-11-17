from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import get_current_user
from ..models import Project, Team, TeamMember, ProjectWaitlist, User, Skill
from ..ai.team_selection import recommend_team
from ..ai.role_suggestions import suggest_roles_for_project
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
	"""
	Team selection that can work with or without a project.
	If project_id is provided, validates it exists.
	If not provided, works for pre-project team formation.
	"""
	if payload.project_id:
		project = db.query(Project).filter(Project.id == payload.project_id, Project.owner_id == current_user.id).first()
		if not project:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

	user_profiles = [profile.model_dump() for profile in payload.candidate_profiles]
	recommendations = recommend_team(user_profiles, payload.required_skills)
	return recommendations


@router.post("/ml/team-selection/pre-project")
def team_selection_pre_project(
	payload: Dict[str, Any],
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""
	Team selection endpoint that doesn't require a project.
	Used for team formation before project creation.
	"""
	from ..models import Skill
	
	required_skills = payload.get("required_skills", [])
	match_mode = payload.get("match_mode", "skill_match")  # skill_match, interest_match
	
	# If no candidate profiles provided, search for users by skills
	if not payload.get("candidate_profiles"):
		if match_mode in ["skill_match", "interest_match"]:
			# Search for users with matching skills
			skill_list = required_skills if required_skills else [
				skill.name for skill in db.query(Skill).filter(Skill.user_id == current_user.id)
			]
			
			# Find users with matching skills
			users_with_skills = (
				db.query(User, Skill)
				.join(Skill, User.id == Skill.user_id)
				.filter(Skill.name.in_([s.capitalize() if isinstance(s, str) else s for s in skill_list]))
				.filter(User.id != current_user.id)
				.filter(User.profile_completed == True)
				.all()
			)
			
			# Group by user
			user_profiles = {}
			for user, skill in users_with_skills:
				if user.id not in user_profiles:
					user_profiles[user.id] = {
						"user_id": user.id,
						"skills": [],
					}
				user_profiles[user.id]["skills"].append(skill.name)
			
			candidate_profiles = list(user_profiles.values())
		else:
			candidate_profiles = []
	else:
		candidate_profiles = payload.get("candidate_profiles", [])
	
	recommendations = recommend_team(candidate_profiles, required_skills)
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

	# Check if team already exists
	existing_team = db.query(Team).filter(Team.project_id == project_id).first()
	if existing_team:
		team = existing_team
		# Remove existing members to reassign
		db.query(TeamMember).filter(TeamMember.team_id == team.id).delete()
	else:
		team = Team(project_id=project_id)
		db.add(team)
		db.flush()

	# Always ensure creator is in the team
	user_ids = payload.user_ids if payload.user_ids else []
	if current_user.id not in user_ids:
		user_ids.append(current_user.id)

	for user_id in user_ids:
		role = payload.role_map.get(user_id) if payload.role_map else None
		# Set creator as Team Leader if no role specified
		if user_id == current_user.id and not role:
			role = "Team Leader"
		db.add(TeamMember(team_id=team.id, user_id=user_id, role=role))

	project.team_id = team.id
	project.team_type = "team" if len(user_ids) > 1 else "solo"
	db.commit()
	db.refresh(team)
	return team


@router.post("/projects/{project_id}/suggest-roles", response_model=Dict[str, Any])
def suggest_roles(
	project_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""
	Suggest roles for team members based on project domain, problem statement, and team size.
	"""
	project = db.query(Project).filter(Project.id == project_id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
	
	# Get team members if team exists
	team_size = 1  # At least the creator
	member_skills_list = []
	
	if project.team_id:
		team = db.query(Team).filter(Team.id == project.team_id).first()
		if team:
			members = db.query(TeamMember).filter(TeamMember.team_id == team.id).all()
			team_size = len(members)
			
			# Get skills for each member
			for member in members:
				skills = [skill.name for skill in db.query(Skill).filter(Skill.user_id == member.user_id)]
				member_skills_list.append({
					"user_id": member.user_id,
					"skills": skills,
				})
	
	# Extract domain and problem from project (you may need to add these fields to Project model)
	# For now, use description to infer
	domain = getattr(project, "domain", "") or ""
	problem_statement = project.description or ""
	
	# Get suggested roles
	suggested_roles = suggest_roles_for_project(
		domain=domain,
		problem_statement=problem_statement,
		team_size=team_size,
		member_skills=member_skills_list
	)
	
	return {
		"suggested_roles": suggested_roles,
		"team_size": team_size,
		"domain": domain,
	}
	

@router.get("/projects/{project_id}/team", response_model=dict[str, Any])
def get_team(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	project = db.query(Project).filter(Project.id == project_id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
	
	# Allow access if user is owner or team member
	if project.owner_id != current_user.id:
		# Check if user is a team member
		if project.team_id:
			team = db.query(Team).filter(Team.id == project.team_id).first()
			if team:
				member = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == current_user.id).first()
				if not member:
					raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view team")
		else:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view team")
	
	if not project.team_id:
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


@router.post("/waitlist/process-expired")
def process_expired_waitlists(db: Session = Depends(get_db)):
	"""
	Process expired waitlists (older than 7 days) and convert them to solo projects.
	This should be called periodically (e.g., via a cron job or scheduled task).
	"""
	expired_threshold = datetime.utcnow() - WAITLIST_DURATION
	
	# Find expired waitlist entries
	expired_entries = (
		db.query(ProjectWaitlist)
		.join(Project, ProjectWaitlist.project_id == Project.id)
		.filter(Project.team_type == "waitlist")
		.filter(ProjectWaitlist.created_at < expired_threshold)
		.all()
	)
	
	processed = []
	for entry in expired_entries:
		project = db.query(Project).filter(Project.id == entry.project_id).first()
		if project and project.team_type == "waitlist":
			# Convert to solo project
			project.team_type = "solo"
			
			# Ensure creator is in the team
			if project.team_id:
				team = db.query(Team).filter(Team.id == project.team_id).first()
				if team:
					# Check if creator is already a member
					existing_member = db.query(TeamMember).filter(
						TeamMember.team_id == team.id,
						TeamMember.user_id == project.owner_id
					).first()
					if not existing_member:
						db.add(TeamMember(team_id=team.id, user_id=project.owner_id, role="Solo Developer"))
			
			# Remove waitlist entry
			db.delete(entry)
			processed.append(project.id)
	
	db.commit()
	return {
		"message": f"Processed {len(processed)} expired waitlists",
		"processed_project_ids": processed,
	}
