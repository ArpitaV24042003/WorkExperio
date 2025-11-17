from __future__ import annotations

from typing import Dict, Any, List
from datetime import datetime, timedelta
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
	
	# Step 2: Find matching team members (optimized and ensures teams are created)
	from sqlalchemy import func, distinct
	
	skill_list = [s.lower() for s in current_user_skills]
	
	# Get user IDs with matching skills (join with User to filter by profile_completed)
	user_ids_with_skills = (
		db.query(distinct(Skill.user_id))
		.join(User, Skill.user_id == User.id)
		.filter(func.lower(Skill.name).in_(skill_list))
		.filter(Skill.user_id != current_user.id)
		.filter(User.profile_completed == True)
		.limit(20)  # Get more candidates for better team formation
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
		
		if users:
			# Get skills for these users
			all_skills = db.query(Skill).filter(Skill.user_id.in_(user_ids_list)).all()
			skills_by_user = {}
			for skill in all_skills:
				if skill.user_id not in skills_by_user:
					skills_by_user[skill.user_id] = []
				skills_by_user[skill.user_id].append(skill.name)
			
			# Calculate match scores and compatibility
			candidates = []
			for user in users:
				user_skills = [s.lower() for s in skills_by_user.get(user.id, [])]
				match_count = len(set(user_skills) & set(skill_list))
				# Calculate diversity (how many unique skills they bring)
				diversity = len(set(user_skills) - set(skill_list))
				# Compatibility score: match + diversity bonus
				compatibility_score = match_count + (diversity * 0.5)
				
				if match_count > 0:  # Must have at least one matching skill
					candidates.append({
						"user_id": user.id,
						"name": user.name,
						"email": user.email,
						"skills": skills_by_user.get(user.id, []),
						"match_score": match_count,
						"compatibility_score": compatibility_score,
					})
			
			# Sort by compatibility (match + diversity)
			candidates.sort(key=lambda x: (x["compatibility_score"], x["match_score"]), reverse=True)
			
			# Select team size based on available candidates and optimal team composition
			# Ideal team: 3-5 members (including creator = 4-6 total)
			optimal_team_size = min(5, max(3, len(candidates)))  # 3-5 additional members
			top_candidates = candidates[:optimal_team_size]
			
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
	# For skill/interest matching, all members are equal collaborators (no "leader")
	# The project owner is just the creator, but all team members have equal roles
	role_map = {}
	
	# Assign roles based on skills and compatibility
	# Creator gets first suggested role (but not "Team Leader" for skill matching)
	creator_role = suggested_roles[0] if suggested_roles else "Team Member"
	if creator_role == "Team Leader" and len(team_member_ids) > 0:
		# If we have team members, use a more collaborative role
		creator_role = suggested_roles[1] if len(suggested_roles) > 1 else "Team Member"
	role_map[current_user.id] = creator_role
	
	# Assign roles to matched team members based on their skills
	for i, member_profile in enumerate(team_member_profiles):
		member_id = member_profile["user_id"]
		member_skills = [s.lower() for s in member_profile.get("skills", [])]
		
		# Assign role based on member's skills
		if any(skill in ["frontend", "react", "vue", "angular", "ui", "design", "css", "html"] for skill in member_skills):
			role_map[member_id] = "Frontend Developer"
		elif any(skill in ["backend", "server", "api", "database", "node", "python", "java", "django", "flask"] for skill in member_skills):
			role_map[member_id] = "Backend Developer"
		elif any(skill in ["data", "ml", "ai", "analytics", "science", "machine learning"] for skill in member_skills):
			role_map[member_id] = "Data Scientist"
		elif i + 1 < len(suggested_roles):
			role_map[member_id] = suggested_roles[i + 1]
		else:
			role_map[member_id] = "Team Member"
	
	# Step 6: Check if user wants to wait or create solo immediately
	wait_for_team = payload.get("wait_for_team", False)  # User's choice to wait
	
	# Step 7: Create project
	# Determine team type: "team" if we have matched members, "waitlist" if waiting, "solo" if none
	has_team = len(team_member_ids) > 0
	
	# If no team found and user hasn't decided yet, return info without creating project
	if not has_team and not wait_for_team and payload.get("wait_for_team") is None:
		# Return response indicating no team found, asking user to decide
		return {
			"project": None,
			"team": None,
			"team_members": [],
			"project_idea": project_idea,
			"match_mode": match_mode,
			"matched_count": 0,
			"team_size": 1,
			"waitlist": False,
			"needs_user_decision": True,  # Flag to indicate user needs to decide
			"message": "No matching team members found. Would you like to wait 7 days for team matching, or create a solo project now?",
		}
	
	if not has_team and wait_for_team:
		# Create project with waitlist status
		project = Project(
			title=project_idea["title"],
			description=project_idea["description"],
			owner_id=current_user.id,
			team_type="waitlist",  # Special status for waiting
			ai_generated=True,
		)
		db.add(project)
		db.flush()
		
		# Add user to waitlist
		waitlist_entry = ProjectWaitlist(
			project_id=project.id,
			user_id=current_user.id,
		)
		db.add(waitlist_entry)
		
		# Create solo team for now (will be updated if team is found)
		team = Team(project_id=project.id)
		db.add(team)
		db.flush()
		
		# Add creator as solo member for now
		db.add(TeamMember(team_id=team.id, user_id=current_user.id, role=creator_role))
		
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
					"user_id": current_user.id,
					"name": current_user.name,
					"role": creator_role,
					"is_creator": True,
				}
			],
			"project_idea": project_idea,
			"match_mode": match_mode,
			"matched_count": 0,
			"team_size": 1,
			"waitlist": True,
			"waitlist_expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
			"message": "You've been added to the waitlist. We'll try to find team members for 7 days. If no team is found, a solo project will be created automatically.",
		}
	
	# Create project normally (with team or solo)
	project = Project(
		title=project_idea["title"],
		description=project_idea["description"],
		owner_id=current_user.id,  # Creator is owner, but all members are equal collaborators
		team_type="team" if has_team else "solo",
		ai_generated=True,
	)
	db.add(project)
	db.flush()
	
	# Step 8: Create team and assign members (always create team, even for solo)
	team = Team(project_id=project.id)
	db.add(team)
	db.flush()
	
	# Add all team members including creator
	all_member_ids = [current_user.id] + team_member_ids
	for user_id in all_member_ids:
		role = role_map.get(user_id, "Team Member")
		db.add(TeamMember(team_id=team.id, user_id=user_id, role=role))
	
	project.team_id = team.id
	project.team_type = "team" if has_team else "solo"
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
				"is_creator": user_id == current_user.id,
			}
			for user_id in all_member_ids
		],
		"project_idea": project_idea,
		"match_mode": match_mode,
		"matched_count": len(team_member_ids),
		"team_size": len(all_member_ids),
		"waitlist": False,
		"message": f"Successfully created team with {len(all_member_ids)} member{'s' if len(all_member_ids) != 1 else ''}" if has_team else "Created solo project (no matching team members found)",
	}

