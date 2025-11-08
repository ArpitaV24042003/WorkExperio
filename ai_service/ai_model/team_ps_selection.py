import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError(
        "❌ GEMINI_API_KEY not set. Please export it before running.")
genai.configure(api_key=api_key)

SYSTEM_PROMPT = """
SYSTEM: You are an expert software engineer, project manager, and technical workflow architect.
Your job is to generate a full, auditable project plan in strict JSON, plus a short human summary.

The user will append INPUT JSON (team + constraints) after this prompt. Do NOT invent people or skills.

--- CORE RULES (MUST FOLLOW) ---
1) You must generate the project_title and problem_statement.
2) You must decide project_deadline_days yourself (realistic, 30–90 days typical). Do NOT use formulas or rely on user hours; justify your choice in the summary.
3) Assign ONLY technical roles and tasks. Forbidden: documentation-only roles/tasks, GitHub repo creation/maintenance/branch protection/labels, or status-reporting/admin tasks.
4) Every member must have meaningful, hands-on technical work that grows their skills (e.g., UI engineering, API/back-end, database schema & optimization, ML model training/inference, DevOps pipelines, infra-as-code, performance/security testing, E2E test automation). PM may exist but must also own technical tasks.
5) Respect the constraints from input: preferred_phases_min/max, suggested_task_count_min/max, max_workload_skew.

--- INSTRUCTIONS ---

A. PROJECT TITLE & PROBLEM STATEMENT
- Generate a clear project_title and a professional problem_statement.
- The problem_statement must include:
  * objective (main goal),
  * scope (explicit inclusions and exclusions),
  * impact (why it matters and to whom).
- Keep it technically achievable for the given team.

B. DEADLINE
- Decide project_deadline_days realistically based on domain complexity and scope (typical range 30–90 days).
- Do NOT compute using formulas or available_hours_per_week; pick a defensible value and justify in the human summary.

C. TEAM ROLE ASSIGNMENT
- Assign each member a technical primary_role (Frontend, Backend, Data/ML, DevOps/Cloud, QA Automation, Security/Perf, DB Engineering, etc.).
- Do NOT assign documentation writer or repo maintainer.
- Provide 1–2 bullet justifications referencing exact skill names/levels from input.
- Ensure everyone has technical contribution with learning opportunity.

D. PHASES & TASK PLAN
- Create N ordered phases within preferred_phases_min/max (from input).
- Ensure total tasks are within suggested_task_count_min/max (from input).
- Every task must be technical and meaningful (examples: implement React views; design REST/GraphQL endpoints; write service/business logic; DB migrations & indexing; containerize services; IaC; CI/CD pipeline definitions; load/perf/security tests; ML data prep/training/inference endpoints).
- EXCLUDE tasks for GitHub repository creation/maintenance and pure documentation.
- Task spec fields (must include all):
  id, title, description, owner, role, skill_used,
  files_or_modules, step_by_step (commands/APIs/pseudocode),
  dependencies, parallelizable, estimated_hours,
  acceptance_criteria, tests_to_run, suggested_branch,
  pr_checklist, notes(optional).
- Avoid overlapping work on the same file/module in the same phase; if unavoidable, add an explicit integration task with clear handoff.

E. INTEGRATION & MERGE STRATEGY
- Define branching model (feature/*, develop, main).
- Specify merge order, conflict handling (integration owner/branch), CI/CD gates, and required PR checks.
- You may define CI/CD pipeline tasks, but do not include GitHub repo creation/maintenance.

F. SCHEDULING & WORKLOAD
- Provide estimated_hours_per_member and compute workload balance.
- Compare max/min against max_workload_skew (from input).
- Provide a week-by-week mapping of phases to calendar weeks within your chosen project_deadline_days.
- If skew exceeds allowed, propose concrete remediation (task reassignments/scope adjustments).

G. RISK, QA & DEPLOYMENT
- List the top 5 risks with mitigations.
- QA plan: unit, integration, E2E, plus domain-specific (perf/security or ML validation).
- Deployment plan: environments, rollout steps, rollback strategy, monitoring/alerts.

H. CONFLICT AVOIDANCE
- Provide module_ownership_map (module paths → owners).
- Provide conflict_check explaining why tasks won’t conflict (file/module boundaries, sequencing, integration tasks).

--- OUTPUT FORMAT (STRICT) ---
Respond in EXACTLY this JSON structure:

{
  "project_title": string,
  "chosen_domain": string,
  "project_deadline_days": integer,
  "problem_statement": { "objective": string, "scope": string, "impact": string },
  "team_roles": [
    { "name": string, "primary_role": string, "justification": [string] }
  ],
  "phases": [
    {
      "phase_id": string,
      "name": string,
      "objective": string,
      "tasks": [
        {
          "id": string,
          "title": string,
          "description": string,
          "owner": string,
          "role": string,
          "skill_used": string,
          "files_or_modules": [string],
          "step_by_step": [string],
          "dependencies": [string],
          "parallelizable": boolean,
          "estimated_hours": integer,
          "acceptance_criteria": [string],
          "tests_to_run": [string],
          "suggested_branch": string,
          "pr_checklist": [string],
          "notes": [string]
        }
      ],
      "deliverables": [string],
      "phase_dependencies": [string]
    }
  ],
  "module_ownership_map": { "<module_path>": "member_name" },
  "integration_plan": [string],
  "merge_strategy": [string],
  "scheduling": {
    "estimated_hours_per_member": { "member_name": integer },
    "timeline_weeks": [ { "week": integer, "phases": [string] } ]
  },
  "risk_areas": [string],
  "qa_plan": [string],
  "deployment_plan": [string],
  "conflict_check": [string],
  "workload_balance": { "max_hours": integer, "min_hours": integer, "skew": number }
}

--- FINAL REQUIREMENT ---
After the JSON, append a human-readable summary (≤200 words) covering:
- problem statement essence, chosen domain, your deadline and rationale,
- roles coverage,
- number of phases,
- how each person’s tasks are technical and support learning.
"""


user_input = {
    "team": [
        {"name": "Ananya Sharma", "skills": {"Python": "Intermediate",
                                             "Machine Learning": "Advanced", "Data Visualization": "Intermediate"}},
        {"name": "Ravi Kumar", "skills": {"Java": "Advanced",
                                          "Spring Boot": "Advanced", "API Development": "Intermediate"}},
        {"name": "Sara Iqbal", "skills": {"Vue.js": "Advanced",
                                          "HTML/CSS": "Intermediate", "UI/UX Design": "Advanced"}}
    ],
    "constraints": {
        "max_workload_skew": 1.4,
        "preferred_phases_min": 4,
        "preferred_phases_max": 12,
        "suggested_task_count_min": 10,
        "suggested_task_count_max": 40
    }
}

prompt = f"""{SYSTEM_PROMPT}

User Input JSON:
{json.dumps(user_input, indent=2)}
"""



def call_gemini(prompt: str):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    try:
        text = response.candidates[0].content.parts[0].text
    except Exception:
        text = response.text

    json_part, summary = None, None
    try:
        if "}" in text:
            json_str = text[:text.rfind("}")+1]
            summary = text[text.rfind("}")+1:].strip()
            json_part = json.loads(json_str)
    except Exception as e:
        json_part = None

    return json_part, summary, text


result_json, summary, raw = call_gemini(prompt)

print("\n========== RAW RESPONSE ==========")
print(raw)

if result_json:
    print("\n========== PARSED JSON ==========")
    print(json.dumps(result_json, indent=2))

if summary:
    print("\n========== HUMAN SUMMARY ==========")
    print(summary)
