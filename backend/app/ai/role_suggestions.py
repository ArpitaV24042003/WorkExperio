from __future__ import annotations

from typing import List, Dict, Any


def suggest_roles_for_project(
	domain: str,
	problem_statement: str,
	team_size: int,
	member_skills: List[Dict[str, Any]] = None
) -> List[str]:
	"""
	Suggest roles for a project based on domain, problem statement, and team size.
	
	Args:
		domain: Project domain (e.g., "Web Development", "Data Science")
		problem_statement: Problem statement or project goal
		team_size: Number of team members
		member_skills: List of dicts with user_id and skills
	
	Returns:
		List of suggested roles
	"""
	domain_lower = domain.lower() if domain else ""
	problem_lower = problem_statement.lower() if problem_statement else ""
	
	# Base roles by domain
	domain_roles = {
		"web development": ["Frontend Developer", "Backend Developer", "Full Stack Developer", "UI/UX Designer", "DevOps Engineer"],
		"data science": ["Data Scientist", "Data Engineer", "ML Engineer", "Data Analyst", "Business Analyst"],
		"mobile app": ["Mobile Developer (iOS)", "Mobile Developer (Android)", "Backend Developer", "UI/UX Designer", "QA Engineer"],
		"ai/ml": ["ML Engineer", "Data Scientist", "AI Researcher", "Backend Developer", "Data Engineer"],
		"full stack": ["Frontend Developer", "Backend Developer", "Full Stack Developer", "DevOps Engineer", "QA Engineer"],
		"e-commerce": ["Frontend Developer", "Backend Developer", "Payment Integration Specialist", "UI/UX Designer", "Security Engineer"],
		"blockchain": ["Blockchain Developer", "Smart Contract Developer", "Backend Developer", "Security Auditor", "Frontend Developer"],
		"iot": ["Embedded Systems Engineer", "Backend Developer", "Mobile Developer", "Hardware Engineer", "Cloud Engineer"],
	}
	
	# Find matching domain roles
	suggested_roles = []
	for key, roles in domain_roles.items():
		if key in domain_lower:
			suggested_roles = roles
			break
	
	# If no domain match, use problem statement keywords
	if not suggested_roles:
		if any(word in problem_lower for word in ["web", "website", "frontend", "ui", "interface"]):
			suggested_roles = ["Frontend Developer", "Backend Developer", "UI/UX Designer"]
		elif any(word in problem_lower for word in ["data", "analytics", "analysis", "machine learning", "ml"]):
			suggested_roles = ["Data Scientist", "Data Engineer", "ML Engineer"]
		elif any(word in problem_lower for word in ["mobile", "app", "ios", "android"]):
			suggested_roles = ["Mobile Developer", "Backend Developer", "UI/UX Designer"]
		else:
			# Default roles
			suggested_roles = ["Developer", "Designer", "Project Manager", "QA Engineer"]
	
	# Adjust based on team size
	if team_size <= 2:
		# Small team - combine roles
		suggested_roles = suggested_roles[:2] if len(suggested_roles) >= 2 else suggested_roles
	elif team_size <= 4:
		# Medium team
		suggested_roles = suggested_roles[:4] if len(suggested_roles) >= 4 else suggested_roles
	else:
		# Large team - can have specialized roles
		suggested_roles = suggested_roles[:5] if len(suggested_roles) >= 5 else suggested_roles
	
	# Always include Team Leader for the creator
	if "Team Leader" not in suggested_roles:
		suggested_roles.insert(0, "Team Leader")
	
	return suggested_roles[:team_size] if team_size > 0 else suggested_roles

