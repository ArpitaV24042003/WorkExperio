from __future__ import annotations

from typing import List, Dict, Any
import re

FAQ_RESPONSES = {
	"what should i do next": "Review the project milestones and pick the next task aligned with your strongest skill.",
	"how to debug": "Reproduce the issue, isolate the failing component, add logging, and write a focused test.",
	"summary": "Here's a quick summary of the recent team chat activity.",
}


def generate_assistant_response(message: str, project_context: Dict[str, Any], conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
	"""
	Generate AI assistant response with conversation context.
	Enhanced to provide more ChatGPT/Gemini-like conversational responses.
	"""
	conversation_history = conversation_history or []
	lowered = message.lower().strip()
	
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
	user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
	assistant_messages = [msg for msg in conversation_history if msg.get("role") == "assistant"]
	
	# If this is a follow-up question, reference previous context
	if len(user_messages) > 1:
		last_user_msg = user_messages[-2]["content"] if len(user_messages) > 1 else ""
		if any(word in lowered for word in ["that", "it", "this", "above", "previous", "earlier", "what about", "and"]):
			response_parts.append(f"Following up on your previous question, ")
	
	# Enhanced response generation with more natural language
	if any(word in lowered for word in ["help", "how", "what", "why", "when", "where", "can you", "could you"]):
		if "code" in lowered or "programming" in lowered or "implement" in lowered:
			response_parts.append("I can help you with coding! Here are some ways I can assist:\n\n")
			response_parts.append("• **Code Review**: Share your code and I'll review it for best practices, potential bugs, and improvements.\n")
			response_parts.append("• **Implementation Help**: I can help you implement features, debug issues, or suggest algorithms.\n")
			response_parts.append("• **Best Practices**: Get recommendations on code structure, design patterns, and optimization.\n\n")
			response_parts.append("What specific coding challenge are you working on?")
		elif "project" in lowered or "plan" in lowered:
			response_parts.append("I can help with project planning and management! Here's what I can do:\n\n")
			response_parts.append("• **Milestone Planning**: Break down your project into manageable milestones.\n")
			response_parts.append("• **Task Prioritization**: Help prioritize tasks based on dependencies and importance.\n")
			response_parts.append("• **Team Coordination**: Suggest ways to improve team collaboration and communication.\n\n")
			if project_context.get("recent_team_messages"):
				response_parts.append("I noticed recent team activity. Would you like me to summarize it or help with a specific aspect?")
			else:
				response_parts.append("What aspect of project planning would you like help with?")
		else:
			response_parts.append("I'm here to help! I can assist with:\n\n")
			response_parts.append("• **Project Planning**: Break down tasks, set milestones, and organize your workflow.\n")
			response_parts.append("• **Coding & Debugging**: Get help with code implementation, debugging, and best practices.\n")
			response_parts.append("• **Team Collaboration**: Coordinate with teammates, manage tasks, and track progress.\n")
			response_parts.append("• **Technical Questions**: Ask about technologies, frameworks, algorithms, or any technical topic.\n\n")
			response_parts.append("What would you like help with today?")
	
	elif "problem" in lowered or "issue" in lowered or "error" in lowered or "bug" in lowered or "not working" in lowered:
		response_parts.append("Let's troubleshoot this together! Here's a systematic approach:\n\n")
		response_parts.append("1. **Reproduce the Issue**: Can you consistently reproduce the problem? What steps lead to it?\n")
		response_parts.append("2. **Check Logs**: Look for error messages, stack traces, or warning logs that might give clues.\n")
		response_parts.append("3. **Isolate the Problem**: Try to narrow down which component or function is causing the issue.\n")
		response_parts.append("4. **Test Hypotheses**: Make small changes and test to see what fixes or worsens the problem.\n\n")
		response_parts.append("Can you share more details about the problem? For example:\n")
		response_parts.append("• What were you trying to do when it occurred?\n")
		response_parts.append("• What error messages (if any) did you see?\n")
		response_parts.append("• What have you already tried to fix it?")
	
	elif "suggest" in lowered or "idea" in lowered or "recommend" in lowered or "what should" in lowered:
		response_parts.append("Based on your project context, here are some suggestions:\n\n")
		response_parts.append("• **Review Milestones**: Check your current progress against planned milestones.\n")
		response_parts.append("• **Team Progress**: Review what your teammates have been working on.\n")
		response_parts.append("• **Identify Blockers**: Look for any tasks that are blocked or need attention.\n")
		response_parts.append("• **Next Steps**: Focus on high-priority tasks that unblock other work.\n\n")
		if project_context.get("suggested_tasks"):
			response_parts.append("Here are some specific tasks you might consider:\n")
			for task in project_context.get("suggested_tasks", [])[:3]:
				response_parts.append(f"• {task}\n")
	
	elif "thank" in lowered or "thanks" in lowered or "appreciate" in lowered:
		response_parts.append("You're very welcome! 😊\n\n")
		response_parts.append("I'm here whenever you need help. Feel free to ask about:\n")
		response_parts.append("• Your project and its progress\n")
		response_parts.append("• Coding questions and debugging\n")
		response_parts.append("• Team coordination and collaboration\n")
		response_parts.append("• Any technical challenges you're facing\n\n")
		response_parts.append("Is there anything else I can help you with?")
	
	elif "explain" in lowered or "what is" in lowered or "tell me about" in lowered:
		response_parts.append("I'd be happy to explain! ")
		if "code" in lowered or "function" in lowered or "algorithm" in lowered:
			response_parts.append("Could you share the specific code, function, or algorithm you'd like me to explain? I can break it down step by step and help you understand how it works.")
		else:
			response_parts.append("Could you provide more details about what specifically you'd like me to explain? I can provide a clear, detailed explanation.")
	
	elif "evaluate" in lowered or "assessment" in lowered or "review" in lowered or "feedback" in lowered:
		response_parts.append("I can help evaluate your work! Here's how I assess understanding and performance:\n\n")
		response_parts.append("**Evaluation Criteria:**\n")
		response_parts.append("• **Code Quality**: Structure, readability, best practices\n")
		response_parts.append("• **Problem Solving**: Approach, logic, efficiency\n")
		response_parts.append("• **Understanding**: Demonstrates grasp of concepts\n")
		response_parts.append("• **Collaboration**: Communication, teamwork, contributions\n\n")
		response_parts.append("To get a comprehensive evaluation, please:\n")
		response_parts.append("1. Share your code or work product\n")
		response_parts.append("2. Describe what you've implemented\n")
		response_parts.append("3. Explain any challenges you faced\n\n")
		response_parts.append("I'll provide detailed feedback on your understanding, code quality, and areas for improvement.")
	
	else:
		# Default contextual response - more conversational
		if len(conversation_history) > 0:
			response_parts.append("I understand. ")
		else:
			response_parts.append("Hello! I'm your AI assistant for this project. ")
		
		if project_context.get("recent_team_messages"):
			response_parts.append("I can see there's been recent team activity. ")
		
		response_parts.append("How can I assist you today? I can help with:\n\n")
		response_parts.append("• **Project Planning**: Organize tasks, set milestones, and plan your workflow\n")
		response_parts.append("• **Coding Help**: Debug issues, review code, or implement features\n")
		response_parts.append("• **Team Coordination**: Coordinate with teammates and track progress\n")
		response_parts.append("• **Technical Questions**: Answer questions about technologies, frameworks, or best practices\n\n")
		response_parts.append("What would you like to work on?")
	
	response = "".join(response_parts)
	if not response.strip():
		response = "Hello! I'm here to help with your project. I can assist with planning, coding, debugging, team coordination, and technical questions. What would you like help with today?"
	
	return {
		"response": response,
		"suggestions": project_context.get("suggested_tasks", []),
	}

