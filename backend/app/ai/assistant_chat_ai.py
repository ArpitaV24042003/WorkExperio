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

	This is a deterministic, LLM-style helper that tries to behave closer to ChatGPT:
	- Reads basic project context (title, description, tasks, team, files)
	- Produces multi-paragraph, concrete guidance instead of short bullet placeholders
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
	assignee_map = {t.get("assignee_id"): [] for t in tasks if t.get("assignee_id")}
	for t in tasks:
		if t.get("assignee_id"):
			assignee_map.setdefault(t["assignee_id"], []).append(t)

	team_roles = {m.get("user_id"): m.get("role") for m in team_members}
	file_names = [f.get("filename") for f in files][:5]

	response_parts: List[str] = []

	# If this is a follow-up question, reference previous context
	user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
	if len(user_messages) > 1 and any(
		word in lowered for word in ["that", "it", "this", "above", "previous", "earlier", "what about", "and"]
	):
		response_parts.append("Picking up from your earlier question, I'll build on that context and go deeper.\n\n")

	# Dedicated branches for different intents
	if any(word in lowered for word in ["bug", "error", "exception", "not working", "crash", "stack trace"]):
		response_parts.append(
			f"Let's debug this step by step in the context of **{project_title}**. "
			"Here's a practical workflow you can follow:\n\n"
		)
		response_parts.append(
			"1) **Reproduce the issue precisely** – write down the exact steps (URL, inputs, clicks) that lead to the error. "
			"If it's backend related, capture the request payload and any logs or stack traces.\n\n"
		)
		response_parts.append(
			"2) **Narrow down the failing area** – is it a React component (state/props), an API call (HTTP 4xx/5xx), or a FastAPI route (validation/db error)? "
			"Add temporary logging around the suspected functions and check which line fails.\n\n"
		)
		response_parts.append(
			"3) **Create a minimal test case** – if possible, isolate the logic into a small function or endpoint and write a focused unit test that reproduces the bug. "
			"This makes it much easier to reason about and fix.\n\n"
		)
		response_parts.append(
			"4) **Propose a concrete fix** – if you paste the specific error message and the related code snippet, I can walk through it line by line and suggest an exact patch "
			"(including updated React code or FastAPI handler) rather than a generic explanation.\n\n"
		)
		response_parts.append(
			"Send me the failing code block and the error output next, and I’ll draft a corrected version with explanations."
		)
	elif any(word in lowered for word in ["plan", "roadmap", "milestone", "architecture"]):
		response_parts.append(
			f"For **{project_title}**, we can design a clear, actionable plan instead of loose ideas.\n\n"
		)
		response_parts.append(
			"**High-level structure:** you already have a React + FastAPI stack, so we can think in terms of frontend features, backend APIs, and data model evolution. "
			"We'll break work into small, shippable slices that can be completed in a few hours each.\n\n"
		)
		if open_tasks:
			response_parts.append(
				f"Currently there are {len(open_tasks)} open tasks and {len(done_tasks)} completed. "
				"Start by grouping open tasks into milestones (e.g., authentication, dashboards, analytics, AI assistant) and order them by dependency.\n\n"
			)
		else:
			response_parts.append(
				"Right now I don't see structured tasks in the context, so we should first define a backlog: authentication, core CRUD, dashboards, "
				"analytics, team features, and AI assistance.\n\n"
			)
		response_parts.append(
			"Next, we can derive a 1–2 week roadmap: "
			"Day 1–2 for tightening auth & persistence, Day 3–4 for project/Task flows, Day 5–6 for analytics and basic charts, Day 7+ for polishing AI interactions. "
			"If you describe your current progress in more detail, I can turn this into a concrete task list with suggested implementation steps."
		)
	elif any(word in lowered for word in ["code", "implement", "example", "snippet", "function", "component"]):
		response_parts.append(
			"I can absolutely help you with concrete code. Below is a generic pattern you can adapt, and if you paste your existing code I can refactor it specifically.\n\n"
		)
		response_parts.append(
			"**Example: React fetch hook pattern** (using async/await and error handling):\n\n"
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
			"    return () => { cancelled = true; };\n"
			"  }, [projectId]);\n\n"
			"  return { data, loading, error };\n"
			"}\n"
			"```\n\n"
		)
		response_parts.append(
			"If you share the specific React component or FastAPI route you’re working on, I can rewrite it in this style and explain every change."
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
				"Open tasks include: "
			)
			for t in open_tasks[:3]:
				title = t.get(\"title\") or \"(untitled)\"
				status = t.get(\"status\") or \"todo\"
				response_parts.append(f\"- {title} [{status}]\\n\")
			response_parts.append(\"\\n\")

		if team_members:
			response_parts.append(
				f\"Your team has {len(team_members)} member(s). Roles I see: \" +
				\", \".join(sorted(set(r for r in team_roles.values() if r))) +
				\".\\n\\n\"
			)

		if file_names:
			response_parts.append(
				\"Some recent files attached to this project are: \" +
				\", \".join(file_names) +
				\".\\n\\n\"
			)

		response_parts.append(
			\"Tell me what you want to focus on right now – for example, I can help you refactor a specific component, design a database model, \"\n"
			\"or break your remaining tasks into smaller, more manageable steps.\\n\"
		)

	response = \"\".join(response_parts)

	# Ensure the reply is reasonably detailed, not a 1–2 word answer
	if len(response.split()) < 60:
		response += (
			\"\\n\\nTo go deeper, paste the relevant piece of code, the exact error message, or the task you're trying to complete. \"\n"
			\"I can then propose a concrete implementation plan and example snippets tailored to your current stack.\"
		)

	return {
		\"response\": response,
		\"suggestions\": project_context.get(\"suggested_tasks\", []),
	}

