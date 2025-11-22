from __future__ import annotations

from typing import List, Dict, Any
import os

from openai import OpenAI


def _build_system_prompt(project_context: Dict[str, Any]) -> str:
	"""
	Construct a rich system prompt so the underlying LLM behaves like a
	project-focused ChatGPT assistant.
	"""
	project_title = project_context.get("project_title") or "your project"
	project_description = project_context.get("project_description") or ""
	tasks = project_context.get("tasks") or []
	team_members = project_context.get("team_members") or []
	files = project_context.get("files") or []

	lines: List[str] = []
	lines.append(
		"You are an expert full‑stack project assistant (like ChatGPT) helping students "
		"collaborate on software, hardware, and IoT projects inside an app called WorkExperio."
	)
	lines.append(
		"Always give **concrete, implementation‑ready answers**: real code, step‑by‑step plans, "
		"debugging strategies, file structures, schedules, and role suggestions."
	)
	lines.append(
		"When you answer coding questions, write idiomatic, production‑quality code for the "
		"described stack (React/Tailwind on the frontend, FastAPI + SQLAlchemy + Postgres on "
		"the backend, unless the user clearly asks for something else)."
	)
	lines.append(
		"If the user’s request is ambiguous or missing critical information, **start by asking "
		"1‑3 precise clarifying questions** before you commit to a solution."
	)
	lines.append("Never answer with placeholders like 'you can do X' without at least one real example.")
	lines.append("Tie your answer to the current project context when possible.\n")

	lines.append(f"Current project title: {project_title}")
	if project_description:
		lines.append(f"Project description: {project_description}")

	if tasks:
		open_tasks = [t for t in tasks if t.get("status") != "done"]
		done_tasks = [t for t in tasks if t.get("status") == "done"]
		lines.append(
			f"Tasks summary: {len(tasks)} total, {len(done_tasks)} completed, "
			f"{len(open_tasks)} still open."
		)

	if team_members:
		lines.append(
			"Team members (user_id → role): "
			+ ", ".join(f"{m.get('user_id')}:{m.get('role') or 'unknown'}" for m in team_members)
		)

	if files:
		lines.append(
			"Recent project files: " + ", ".join(f.get("filename", "?") for f in files[:10])
		)

	lines.append(
		"\nWhen asked for code, return complete functions/components/routes, not just fragments. "
		"Use markdown formatting with ```language fences for code blocks."
	)
	lines.append(
		"\nIMPORTANT: Your responses can contain multiple types of content in a single message:"
	)
	lines.append(
		"- Explanatory paragraphs (regular text)"
	)
	lines.append(
		"- Code blocks (```language ... ```)"
	)
	lines.append(
		"- Multiple code blocks separated by explanations"
	)
	lines.append(
		"- Lists, bullet points, and formatted text"
	)
	lines.append(
		"Format your responses naturally, mixing text and code as needed. Use proper markdown syntax."
	)

	return "\n".join(lines)


def generate_assistant_response(
	message: str,
	project_context: Dict[str, Any],
	conversation_history: List[Dict[str, str]] | None = None,
) -> Dict[str, Any]:
	"""
	Generate a context-aware assistant response.

	If OPENAI_API_KEY is configured, this will call a real ChatGPT-compatible model
	via the OpenAI client. If not, it falls back to a simple, local heuristic reply.
	"""
	conversation_history = conversation_history or []
	api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_WORKEXPERIO")

	# If an API key is available, call a real ChatGPT-like model.
	if api_key:
		client = OpenAI(api_key=api_key)
		system_prompt = _build_system_prompt(project_context)

		messages_payload: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

		# Include full conversation history for multi-turn dialogue
		for item in conversation_history:
			role = item.get("role") or "user"
			if role not in {"user", "assistant", "system"}:
				role = "user"
			content = item.get("content", "").strip()
			if content:  # Only add non-empty messages
				messages_payload.append({"role": role, "content": content})

		messages_payload.append({"role": "user", "content": message})

		chat = client.chat.completions.create(
			model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
			messages=messages_payload,
			temperature=0.2,
		)

		reply_text = chat.choices[0].message.content or ""
		
		return {
			"response": reply_text.strip(),
			"suggestions": project_context.get("suggested_tasks", []),
		}

	# Fallback: simple contextual text if no LLM is configured.
	project_title = project_context.get("project_title") or "your project"
	project_description = project_context.get("project_description") or ""
	tasks = project_context.get("tasks") or []
	open_tasks = [t for t in tasks if t.get("status") != "done"]
	done_tasks = [t for t in tasks if t.get("status") == "done"]

	parts: List[str] = []
	parts.append(
		f"(LLM not configured – using local fallback.) You're working on **{project_title}**.\n"
	)
	if project_description:
		parts.append(project_description.strip() + "\n\n")

	if tasks:
		parts.append(
			f"There are {len(tasks)} tasks ({len(done_tasks)} done, {len(open_tasks)} open). "
			"Focus on one or two high‑impact tasks at a time.\n\n"
		)

	parts.append(
		"I can't call a full ChatGPT model without an API key, but you can add one via the "
		"`OPENAI_API_KEY` env var on the backend and the assistant will start returning rich, "
		"model‑generated answers.\n"
	)

	return {"response": "".join(parts), "suggestions": project_context.get("suggested_tasks", [])}

