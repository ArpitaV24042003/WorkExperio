from __future__ import annotations

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import get_current_user
from ..models import Project, Team, TeamMember, User, Skill, ProjectWaitlist
from ..ai.team_selection import recommend_team
from ..ai.project_generator import generate_project_idea, generate_multiple_project_ideas
from ..ai.role_suggestions import suggest_roles_for_project
from ..schemas import ProjectCreate, ProjectRead

router = APIRouter()


@router.post("/auto-create-project-with-team")
async def auto_create_project_with_team(
	payload: Dict[str, Any],
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""
	Fully automated AI-powered project creation with team formation.
	This endpoint:
	1. Finds team members by skills/interests
	2. Assigns roles automatically
	3. Generates project idea
	4. Creates project
	5. Assigns team to project
	
	All in one automated flow.
	"""
	match_mode = payload.get("match_mode", "skill_match")  # skill_match or interest_match
	domain = payload.get("domain", "")
	problem_statement = payload.get("problem_statement", "")
	
	# Step 1: Get current user's skills
	current_user_skills = [skill.name for skill in db.query(Skill).filter(Skill.user_id == current_user.id)]
	if not current_user_skills:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Please add skills to your profile first"
		)
	
	# Step 2: Find matching team members
	from sqlalchemy import func, distinct
	
	skill_list = [s.lower() for s in current_user_skills]
	
	# Get user IDs with matching skills
	user_ids_with_skills = (
		db.query(distinct(Skill.user_id))
		.filter(func.lower(Skill.name).in_(skill_list))
		.filter(Skill.user_id != current_user.id)
		.filter(User.profile_completed == True)
		.limit(10)
		.all()
	)
	
	team_member_ids = []
	team_member_profiles = []
	
	if user_ids_with_skills:
		user_ids_list = [uid[0] for uid in user_ids_with_skills]
		
		# Get users with completed profiles
		users = (
			db.query(User)
			.filter(User.id.in_(user_ids_list))
			.filter(User.profile_completed == True)
			.all()
		)
		
		# Get skills for these users
		all_skills = db.query(Skill).filter(Skill.user_id.in_(user_ids_list)).all()
		skills_by_user = {}
		for skill in all_skills:
			if skill.user_id not in skills_by_user:
				skills_by_user[skill.user_id] = []
			skills_by_user[skill.user_id].append(skill.name)
		
		# Calculate match scores and select top 3
		candidates = []
		for user in users:
			user_skills = [s.lower() for s in skills_by_user.get(user.id, [])]
			match_count = len(set(user_skills) & set(skill_list))
			if match_count > 0:
				candidates.append({
					"user_id": user.id,
					"name": user.name,
					"email": user.email,
					"skills": skills_by_user.get(user.id, []),
					"match_score": match_count,
				})
		
		candidates.sort(key=lambda x: x["match_score"], reverse=True)
		top_candidates = candidates[:3]  # Top 3 matches
		
		team_member_ids = [c["user_id"] for c in top_candidates]
		team_member_profiles = top_candidates
	
	# Step 3: Generate project idea with team skills
	all_skills_set = set(current_user_skills)
	for member in team_member_profiles:
		all_skills_set.update(member.get("skills", []))
	
	all_skills_list = list(all_skills_set)
	
	# Generate project idea
	if domain and problem_statement:
		project_idea = generate_project_idea(
			skills=all_skills_list,
			experience_level="intermediate",
			domain=domain,
			problem_statement=problem_statement
		)
	else:
		# Generate multiple ideas and pick the best one
		ideas = generate_multiple_project_ideas(
			skills=all_skills_list,
			experience_level="intermediate",
			domain=domain,
			problem_statement=problem_statement,
			count=3
		)
		project_idea = ideas[0] if ideas else {
			"title": "Collaborative Project",
			"description": "A project to build something great together",
			"milestones": ["Planning", "Development", "Testing", "Deployment"]
		}
	
	# Step 4: Suggest roles
	team_size = len(team_member_ids) + 1  # Include creator
	member_skills_list = [{"user_id": current_user.id, "skills": current_user_skills}]
	for member in team_member_profiles:
		member_skills_list.append({
			"user_id": member["user_id"],
			"skills": member.get("skills", [])
		})
	
	suggested_roles = suggest_roles_for_project(
		domain=domain,
		problem_statement=problem_statement or project_idea.get("description", ""),
		team_size=team_size,
		member_skills=member_skills_list
	)
	
	# Step 5: Assign roles to team members
	role_map = {current_user.id: "Team Leader"}
	for i, member_id in enumerate(team_member_ids):
		if i < len(suggested_roles) - 1:  # -1 because Team Leader is already assigned
			role_map[member_id] = suggested_roles[i + 1] if i + 1 < len(suggested_roles) else "Team Member"
		else:
			role_map[member_id] = "Team Member"
	
	# Step 6: Create project
	project = Project(
		title=project_idea["title"],
		description=project_idea["description"],
		owner_id=current_user.id,
		team_type="team" if team_member_ids else "solo",
		ai_generated=True,
	)
	db.add(project)
	db.flush()
	
	# Step 7: Create team and assign members
	team = Team(project_id=project.id)
	db.add(team)
	db.flush()
	
	# Add all team members including creator
	all_member_ids = [current_user.id] + team_member_ids
	for user_id in all_member_ids:
		role = role_map.get(user_id, "Team Member")
		db.add(TeamMember(team_id=team.id, user_id=user_id, role=role))
	
	project.team_id = team.id
	db.commit()
	db.refresh(project)
	db.refresh(team)
	
	return {
		"project": ProjectRead.model_validate(project),
		"team": {
			"id": team.id,
			"project_id": project.id,
		},
		"team_members": [
			{
				"user_id": user_id,
				"name": next((m["name"] for m in team_member_profiles if m["user_id"] == user_id), current_user.name if user_id == current_user.id else "Unknown"),
				"role": role_map.get(user_id, "Team Member"),
			}
			for user_id in all_member_ids
		],
		"project_idea": project_idea,
		"match_mode": match_mode,
		"matched_count": len(team_member_ids),
	}

