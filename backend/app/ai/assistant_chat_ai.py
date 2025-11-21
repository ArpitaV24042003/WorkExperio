from __future__ import annotations

from typing import List, Dict, Any
import re

FAQ_RESPONSES = {
	"what should i do next": "Review the project milestones and pick the next task aligned with your strongest skill.",
	"how to debug": "Reproduce the issue, isolate the failing component, add logging, and write a focused test.",
	"summary": "Here's a quick summary of the recent team chat activity.",
}


def generate_assistant_response(
	message: str,
	project_context: Dict[str, Any],
	conversation_history: List[Dict[str, str]] | None = None,
) -> Dict[str, Any]:
	"""
	Generate a deterministic, context-aware assistant response.

	This does not call an external LLM, but it tries to mimic a helpful ChatGPT-style
	reply using project metadata (title, description, tasks, team, files).
	"""
	conversation_history = conversation_history or []
	lowered = message.lower().strip()

	project_title = project_context.get("project_title") or "your project"
	project_description = project_context.get("project_description") or ""
	tasks = project_context.get("tasks") or []
	team_members = project_context.get("team_members") or []
	files = project_context.get("files") or []

	# Build context summary strings
	open_tasks = [t for t in tasks if t.get("status") != "done"]
	done_tasks = [t for t in tasks if t.get("status") == "done"]
	team_roles = {m.get("user_id"): m.get("role") for m in team_members}
	file_names = [f.get("filename") for f in files][:5]

	response_parts: List[str] = []

	# If this is a follow-up question, reference previous context
	user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
	if len(user_messages) > 1 and any(
		word in lowered
		for word in ["that", "it", "this", "above", "previous", "earlier", "what about", "and"]
	):
		response_parts.append(
			"Picking up from your earlier question, I'll build on that context and go deeper.\n\n"
		)

	# Intent branches
	if any(word in lowered for word in ["bug", "error", "exception", "not working", "crash", "stack trace"]):
		response_parts.append(
			f"Let's debug this step by step in the context of **{project_title}**.\n\n"
		)
		response_parts.append(
			"1) **Reproduce the issue precisely** – capture the exact route, payload, and user actions.\n"
			"2) **Narrow down the failing area** – is it a React component, an API call, or a FastAPI route?\n"
			"3) **Add temporary logging** around the suspected lines to see what values you actually get.\n"
			"4) **Create a minimal test case** that focuses only on the broken behaviour.\n\n"
		)
		response_parts.append(
			"Paste the specific error message and the related code (component or route), and I can propose an exact patch."
		)
	elif any(word in lowered for word in ["plan", "roadmap", "milestone", "architecture"]):
		response_parts.append(
			f"For **{project_title}**, we can design a clear, actionable plan instead of loose ideas.\n\n"
		)
		response_parts.append(
			"Start by grouping work into slices: authentication & persistence, core CRUD and dashboards, "
			"analytics & charts, and finally AI assistance and polishing. "
		)
		if open_tasks:
			response_parts.append(
				f"There are currently {len(open_tasks)} open tasks and {len(done_tasks)} completed. "
				"Use those as your initial backlog and assign them to milestones in order of dependency.\n\n"
			)
		else:
			response_parts.append(
				"Right now I don't see structured tasks in the context, so we should first define a backlog from your requirements.\n\n"
			)
		response_parts.append(
			"If you describe your current progress in more detail, I can turn it into a concrete checklist with suggested implementation order."
		)
	elif any(word in lowered for word in ["code", "implement", "example", "snippet", "function", "component"]):
		response_parts.append(
			"I can help you with concrete code. Here's a generic React data-loading pattern you can adapt:\n\n"
		)
		response_parts.append(
			"```jsx\n"
			"import { useEffect, useState } from \"react\";\n"
			"import { apiClient } from \"../lib/api\";\n\n"
			"export function useProject(projectId) {\n"
			"  const [data, setData] = useState(null);\n"
			"  const [loading, setLoading] = useState(true);\n"
			"  const [error, setError] = useState(\"\");\n\n"
			"  useEffect(() => {\n"
			"    let cancelled = false;\n"
			"    async function load() {\n"
			"      setLoading(true);\n"
			"      setError(\"\");\n"
			"      try {\n"
			"        const res = await apiClient.get(`/projects/${projectId}`);\n"
			"        if (!cancelled) setData(res.data);\n"
			"      } catch (err) {\n"
			"        if (!cancelled) setError(err.message || \"Failed to load project\");\n"
			"      } finally {\n"
			"        if (!cancelled) setLoading(false);\n"
			"      }\n"
			"    }\n"
			"    load();\n"
			"    return () => {\n"
			"      cancelled = true;\n"
			"    };\n"
			"  }, [projectId]);\n\n"
			"  return { data, loading, error };\n"
			"}\n"
			"```\n\n"
		)
		response_parts.append(
			"Share the specific component or endpoint you're working on and I can refactor it in this style, explaining each step."
		)
	else:
		# Default contextual response – summarize context and invite a focused question
		intro = f"You're working on **{project_title}**"
		if project_description:
			intro += f", which is described as: {project_description.strip()}."
		else:
			intro += "."
		response_parts.append(intro + "\n\n")

		if tasks:
			response_parts.append(
				f"There are currently {len(tasks)} tasks in the project "
				f"({len(done_tasks)} completed, {len(open_tasks)} still open). "
				"Some open tasks include:\n"
			)
			for t in open_tasks[:3]:
				title = t.get("title") or "(untitled)"
				status = t.get("status") or "todo"
				response_parts.append(f"- {title} [{status}]\n")
			response_parts.append("\n")

		if team_members:
			roles_list = sorted(set(r for r in team_roles.values() if r))
			roles_text = ", ".join(roles_list) if roles_list else "not yet defined"
			response_parts.append(
				f"Your team has {len(team_members)} member(s). Roles I see: {roles_text}.\n\n"
			)

		if file_names:
			response_parts.append(
				"Some recent files attached to this project are: "
				+ ", ".join(file_names)
				+ ".\n\n"
			)

		response_parts.append(
			"Tell me what you want to focus on right now – for example, I can help you refactor a specific component, "
			"design a database model, or break your remaining tasks into smaller, more manageable steps.\n"
		)

	response = "".join(response_parts)

	# Ensure the reply is reasonably detailed, not a 1–2 word answer
	if len(response.split()) < 60:
		response += (
			"\n\nTo go deeper, paste the relevant piece of code, the exact error message, "
			"or the task you're trying to complete. I can then propose a concrete implementation "
			"plan and example snippets tailored to your current stack."
		)

	return {
		"response": response,
		"suggestions": project_context.get("suggested_tasks", []),
	}

