from __future__ import annotations

from typing import List, Dict, Any

FAQ_RESPONSES = {
	"what should i do next": "Review the project milestones and pick the next task aligned with your strongest skill.",
	"how to debug": "Reproduce the issue, isolate the failing component, add logging, and write a focused test.",
	"summary": "Here's a quick summary of the recent team chat activity.",
}


def generate_assistant_response(message: str, project_context: Dict[str, Any]) -> Dict[str, Any]:
	lowered = message.lower()
	for key, response in FAQ_RESPONSES.items():
		if key in lowered:
			return {
				"response": response,
				"suggestions": project_context.get("suggested_tasks", []),
			}

	return {
		"response": "Focus on collaboration, keep your tasks updated, and communicate blockers early.",
		"suggestions": project_context.get("suggested_tasks", []),
	}

