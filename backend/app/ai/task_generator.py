from __future__ import annotations

from typing import List, Dict, Any
import os
import json

from openai import OpenAI


def generate_tasks_from_project(
	project_title: str,
	project_description: str,
	existing_tasks: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
	"""
	Automatically generate a complete task schedule from project description.
	
	This acts as an intelligent project manager, breaking down the main goal
	into smaller, actionable sub-tasks with dependencies and timeframes.
	"""
	existing_tasks = existing_tasks or []
	api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_WORKEXPERIO")
	
	if not api_key:
		# Fallback: generate basic tasks from keywords
		return _generate_basic_tasks_fallback(project_title, project_description)
	
	try:
		client = OpenAI(api_key=api_key)
		
		system_prompt = """You are an expert project manager. Your job is to break down software projects into actionable tasks.

Given a project title and description, generate a comprehensive list of tasks that need to be completed.
Each task should be:
- Specific and actionable
- Have a clear title and description
- Include an estimated time in hours (2-40 hours per task)
- Be ordered logically (dependencies should be considered)

Return ONLY a valid JSON array of tasks, no other text. Each task should have:
{
  "title": "Task title",
  "description": "Detailed description of what needs to be done",
  "estimated_hours": 8.0,
  "priority": "high|medium|low"
}

Example output:
[
  {"title": "Set up project structure", "description": "Create folder structure, initialize package.json, set up build tools", "estimated_hours": 4.0, "priority": "high"},
  {"title": "Design database schema", "description": "Create ER diagram and define all tables and relationships", "estimated_hours": 6.0, "priority": "high"}
]"""
		
		user_prompt = f"""Project Title: {project_title}

Project Description:
{project_description}

Existing Tasks:
{json.dumps(existing_tasks, indent=2) if existing_tasks else "None"}

Generate a comprehensive task breakdown for this project. If there are existing tasks, focus on filling gaps or adding missing steps."""
		
		response = client.chat.completions.create(
			model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
			messages=[
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": user_prompt}
			],
			temperature=0.3,
			response_format={"type": "json_object"} if os.getenv("OPENAI_MODEL", "").startswith("gpt-4") else None,
		)
		
		content = response.choices[0].message.content or "{}"
		
		# Try to parse as JSON
		try:
			# If response is wrapped in a JSON object
			parsed = json.loads(content)
			if isinstance(parsed, dict) and "tasks" in parsed:
				tasks = parsed["tasks"]
			elif isinstance(parsed, list):
				tasks = parsed
			else:
				tasks = [parsed] if parsed else []
		except json.JSONDecodeError:
			# Try to extract JSON array from text
			import re
			json_match = re.search(r'\[.*\]', content, re.DOTALL)
			if json_match:
				tasks = json.loads(json_match.group())
			else:
				# Fallback to basic tasks
				return _generate_basic_tasks_fallback(project_title, project_description)
		
		# Validate and format tasks
		formatted_tasks = []
		for task in tasks:
			if isinstance(task, dict) and "title" in task:
				formatted_tasks.append({
					"title": task.get("title", ""),
					"description": task.get("description", ""),
					"estimated_hours": float(task.get("estimated_hours", 8.0)),
					"priority": task.get("priority", "medium"),
				})
		
		return formatted_tasks if formatted_tasks else _generate_basic_tasks_fallback(project_title, project_description)
		
	except Exception as e:
		import logging
		logger = logging.getLogger(__name__)
		logger.error(f"Error generating tasks with AI: {e}")
		return _generate_basic_tasks_fallback(project_title, project_description)


def _generate_basic_tasks_fallback(project_title: str, project_description: str) -> List[Dict[str, Any]]:
	"""Fallback task generator when AI is not available."""
	tasks = [
		{
			"title": "Project Setup",
			"description": "Set up project structure, dependencies, and development environment",
			"estimated_hours": 4.0,
			"priority": "high",
		},
		{
			"title": "Design & Planning",
			"description": "Create design documents, wireframes, and technical specifications",
			"estimated_hours": 8.0,
			"priority": "high",
		},
		{
			"title": "Core Implementation",
			"description": "Implement core features and functionality",
			"estimated_hours": 16.0,
			"priority": "high",
		},
		{
			"title": "Testing & Quality Assurance",
			"description": "Write and run tests, fix bugs, ensure quality",
			"estimated_hours": 8.0,
			"priority": "medium",
		},
		{
			"title": "Documentation & Deployment",
			"description": "Write documentation and deploy the project",
			"estimated_hours": 4.0,
			"priority": "medium",
		},
	]
	return tasks

