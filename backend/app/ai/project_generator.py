from __future__ import annotations

from typing import Dict, Any, List
import random

PROJECT_TEMPLATES = [
	{
		"title": "AI-Powered Study Buddy",
		"description": "Build a smart assistant that curates study plans and provides real-time Q&A for students.",
		"milestones": ["Requirements Gathering", "Prototype AI Engine", "Frontend Integration", "User Testing"],
		"domains": ["AI/ML", "Education", "Web Development"],
	},
	{
		"title": "Collaborative Portfolio Builder",
		"description": "Create a platform for students to co-author portfolio projects and showcase achievements.",
		"milestones": ["Design System", "Resume Parser Integration", "Collaboration Tools", "Deployment"],
		"domains": ["Web Development", "Design", "Full Stack"],
	},
	{
		"title": "Skill-based Project Matcher",
		"description": "Develop a recommendation engine that matches students to projects using skill graphs.",
		"milestones": ["Data Modeling", "Match Algorithm", "Dashboard UI", "Insights & Reporting"],
		"domains": ["Data Science", "AI/ML", "Web Development"],
	},
	{
		"title": "Real-time Collaboration Platform",
		"description": "Build a platform for real-time code collaboration with integrated chat and version control.",
		"milestones": ["WebSocket Setup", "Code Editor Integration", "Version Control", "Deployment"],
		"domains": ["Web Development", "Full Stack", "Backend"],
	},
	{
		"title": "Data Analytics Dashboard",
		"description": "Create an interactive dashboard for visualizing and analyzing complex datasets.",
		"milestones": ["Data Pipeline", "Visualization Components", "Dashboard UI", "Performance Optimization"],
		"domains": ["Data Science", "Frontend", "Visualization"],
	},
	{
		"title": "Mobile Learning App",
		"description": "Develop a mobile application for on-the-go learning with offline capabilities.",
		"milestones": ["UI/UX Design", "Mobile Framework Setup", "Offline Storage", "App Store Deployment"],
		"domains": ["Mobile Development", "Mobile App", "React Native"],
	},
	{
		"title": "E-commerce Platform",
		"description": "Build a full-featured e-commerce platform with payment integration and inventory management.",
		"milestones": ["Product Catalog", "Shopping Cart", "Payment Gateway", "Order Management"],
		"domains": ["Web Development", "Full Stack", "E-commerce"],
	},
	{
		"title": "Social Network for Professionals",
		"description": "Create a professional networking platform with profile matching and job recommendations.",
		"milestones": ["User Profiles", "Matching Algorithm", "Messaging System", "Recommendation Engine"],
		"domains": ["Web Development", "Social Media", "Full Stack"],
	},
	{
		"title": "IoT Home Automation System",
		"description": "Develop a system to control and monitor home devices through a web and mobile interface.",
		"milestones": ["Hardware Integration", "API Development", "Mobile App", "Security Implementation"],
		"domains": ["IoT", "Embedded Systems", "Full Stack"],
	},
	{
		"title": "Blockchain Voting System",
		"description": "Create a secure, transparent voting system using blockchain technology.",
		"milestones": ["Blockchain Setup", "Smart Contracts", "Frontend Interface", "Security Audit"],
		"domains": ["Blockchain", "Web3", "Security"],
	},
]


def generate_project_idea(skills: List[str], experience_level: str, domain: str = None, problem_statement: str = None) -> Dict[str, Any]:
	"""
	Generate a project idea based on skills, experience, domain, and problem statement.
	Returns a single project idea.
	"""
	# Filter templates by domain if provided
	available_templates = PROJECT_TEMPLATES
	if domain:
		domain_lower = domain.lower()
		domain_matches = [t for t in PROJECT_TEMPLATES if any(d.lower() in domain_lower or domain_lower in d.lower() for d in t.get("domains", []))]
		if domain_matches:
			available_templates = domain_matches
	
	# Select a template (randomly for variety)
	template = random.choice(available_templates)
	
	# Customize description based on problem statement
	description = template["description"]
	if problem_statement:
		description = f"{description} Focus: {problem_statement[:100]}"
	
	# Add skills context
	if skills:
		description += f" Leveraging skills: {', '.join(skills[:5])}."
	
	return {
		"title": template["title"],
		"description": description,
		"milestones": template["milestones"],
		"suggested_tasks": [
			{
				"name": milestone,
				"description": f"Complete the milestone '{milestone}' focusing on {', '.join(skills[:3]) if skills else 'core skills'}.",
			}
			for milestone in template["milestones"]
		],
	}


def generate_multiple_project_ideas(skills: List[str], experience_level: str, domain: str = None, problem_statement: str = None, count: int = 3) -> List[Dict[str, Any]]:
	"""
	Generate multiple different project ideas.
	"""
	ideas = []
	used_templates = set()
	
	# Filter templates by domain if provided
	available_templates = PROJECT_TEMPLATES
	if domain:
		domain_lower = domain.lower()
		domain_matches = [t for t in PROJECT_TEMPLATES if any(d.lower() in domain_lower or domain_lower in d.lower() for d in t.get("domains", []))]
		if domain_matches:
			available_templates = domain_matches
	
	# Shuffle to get variety
	templates = available_templates.copy()
	random.shuffle(templates)
	
	for i in range(min(count, len(templates))):
		template = templates[i]
		# Customize description
		description = template["description"]
		if problem_statement:
			description = f"{description} Focus: {problem_statement[:100]}"
		if skills:
			description += f" Leveraging skills: {', '.join(skills[:5])}."
		
		ideas.append({
			"title": template["title"],
			"description": description,
			"milestones": template["milestones"],
			"suggested_tasks": [
				{
					"name": milestone,
					"description": f"Complete the milestone '{milestone}' focusing on {', '.join(skills[:3]) if skills else 'core skills'}.",
				}
				for milestone in template["milestones"]
			],
		})
	
	return ideas

