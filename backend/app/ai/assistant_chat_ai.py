from __future__ import annotations

from typing import List, Dict, Any

FAQ_RESPONSES = {
	"what should i do next": "Review the project milestones and pick the next task aligned with your strongest skill.",
	"how to debug": "Reproduce the issue, isolate the failing component, add logging, and write a focused test.",
	"summary": "Here's a quick summary of the recent team chat activity.",
}


def generate_assistant_response(message: str, project_context: Dict[str, Any], conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
	"""
	Generate AI assistant response with conversation context.
	Uses conversation history to provide contextual, conversational responses.
	"""
	conversation_history = conversation_history or []
	lowered = message.lower()
	
	# Check for FAQ matches first
	for key, response in FAQ_RESPONSES.items():
		if key in lowered:
			return {
				"response": response,
				"suggestions": project_context.get("suggested_tasks", []),
			}
	
	# Build context-aware response based on conversation history
	response_parts = []
	
	# Analyze conversation history for context
	if conversation_history:
		# Count messages to understand conversation depth
		user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
		assistant_messages = [msg for msg in conversation_history if msg.get("role") == "assistant"]
		
		# If this is a follow-up question, reference previous context
		if len(user_messages) > 1:
			last_user_msg = user_messages[-2]["content"] if len(user_messages) > 1 else ""
			if any(word in lowered for word in ["that", "it", "this", "above", "previous", "earlier"]):
				response_parts.append(f"Based on our previous discussion about '{last_user_msg[:50]}...', ")
	
	# Generate contextual response
	if "help" in lowered or "how" in lowered or "?" in message:
		response_parts.append("I can help you with project planning, debugging, code suggestions, and team coordination. ")
		if project_context.get("recent_team_messages"):
			response_parts.append("I noticed recent team activity. Would you like me to summarize it or help with a specific task?")
		else:
			response_parts.append("What specific area would you like assistance with?")
	elif "problem" in lowered or "issue" in lowered or "error" in lowered:
		response_parts.append("Let's troubleshoot this step by step. Can you share more details about the problem? ")
		response_parts.append("I can help with debugging strategies, code review, or finding solutions.")
	elif "suggest" in lowered or "idea" in lowered or "recommend" in lowered:
		response_parts.append("Here are some suggestions based on your project context: ")
		response_parts.append("Consider reviewing your milestones, checking team progress, and identifying any blockers.")
	elif "thank" in lowered or "thanks" in lowered:
		response_parts.append("You're welcome! I'm here whenever you need help. Feel free to ask about your project, coding questions, or team coordination.")
	else:
		# Default contextual response
		response_parts.append("I understand. ")
		if project_context.get("recent_team_messages"):
			response_parts.append("I can see there's been recent team activity. ")
		response_parts.append("How can I assist you further? I can help with project planning, debugging, code suggestions, or team coordination.")
	
	response = "".join(response_parts)
	if not response.strip():
		response = "Focus on collaboration, keep your tasks updated, and communicate blockers early. How can I help you today?"
	
	return {
		"response": response,
		"suggestions": project_context.get("suggested_tasks", []),
	}

