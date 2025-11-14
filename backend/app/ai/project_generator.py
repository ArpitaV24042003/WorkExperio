from __future__ import annotations

from typing import Dict, Any, List

PROJECT_TEMPLATES = [
	{
		"title": "AI-Powered Study Buddy",
		"description": "Build a smart assistant that curates study plans and provides real-time Q&A for students.",
		"milestones": ["Requirements Gathering", "Prototype AI Engine", "Frontend Integration", "User Testing"],
	},
	{
		"title": "Collaborative Portfolio Builder",
		"description": "Create a platform for students to co-author portfolio projects and showcase achievements.",
		"milestones": ["Design System", "Resume Parser Integration", "Collaboration Tools", "Deployment"],
	},
	{
		"title": "Skill-based Project Matcher",
		"description": "Develop a recommendation engine that matches students to projects using skill graphs.",
		"milestones": ["Data Modeling", "Match Algorithm", "Dashboard UI", "Insights & Reporting"],
	},
]


def generate_project_idea(skills: List[str], experience_level: str) -> Dict[str, Any]:
	index = len("".join(skills) + experience_level) % len(PROJECT_TEMPLATES)
	template = PROJECT_TEMPLATES[index]
	return {
		"title": template["title"],
		"description": f"{template['description']} Tailored for {experience_level} level leveraging skills: {', '.join(skills)}.",
		"milestones": template["milestones"],
		"suggested_tasks": [
			{
				"name": milestone,
				"description": f"Complete the milestone '{milestone}' focusing on {', '.join(skills[:3]) or 'core skills'}.",
			}
			for milestone in template["milestones"]
		],
	}

