// Centralized AI helpers. Each tries a "preferred" endpoint first,
// then falls back to your earlier routes so you don’t break existing backends.

import { apiRequest } from "./api";

// ---- RESUME PARSING ----
export async function aiParseResume(file) {
  const form = new FormData();
  form.append("resume", file);

  // Preferred: /ai/resume-parse
  try {
    return await apiRequest("/ai/resume-parse", "POST", form);
  } catch {
    // Fallback: /resumes/parse
    return await apiRequest("/resumes/parse", "POST", form);
  }
}

// ---- TEAM FORMATION (suggest teammates / roles) ----
export async function aiFormTeam({ domain, skillLevel, seedMembers = [] }) {
  // Preferred
  try {
    return await apiRequest("/ai/team/formation", "POST", {
      domain,
      skillLevel,
      seedMembers, // [{email|id|name, skills:[]}]
    });
  } catch {
    // Fallback to older endpoint (reuse your existing LLM if needed)
    return await apiRequest("/make-prediction", "POST", {
      domain,
      skillLevel,
      teammates: seedMembers.map((m) => m.email || m.id || m.name).join(", "),
      purpose: "team_formation",
    });
  }
}

// ---- TEAM PROBLEM-STATEMENT SELECTION ----
export async function aiSelectProblemStatements({
  domain,
  skillLevel,
  team = [],
}) {
  // returns { options: [{id, title, brief}], recommendedId }
  try {
    return await apiRequest("/ai/team/ps-selection", "POST", {
      domain,
      skillLevel,
      team,
    });
  } catch {
    // Fallback: synthesize from /make-prediction (if it returns a single PS, wrap as one option)
    const one = await apiRequest("/make-prediction", "POST", {
      domain,
      skillLevel,
      teammates: team.map((t) => t.name || t.email).join(", "),
      purpose: "ps_selection",
    });
    const title = one?.problemStatement || "Auto-generated Problem Statement";
    const brief = one?.details || "Auto-generated details.";
    return { options: [{ id: "ps1", title, brief }], recommendedId: "ps1" };
  }
}

// ---- PROJECT PLAN (LLM) ----
export async function aiGeneratePlan({
  domain,
  skillLevel,
  team = [],
  problemStatement,
}) {
  // returns { problemStatement, details, taskDetails }
  try {
    return await apiRequest("/ai/plan", "POST", {
      domain,
      skillLevel,
      team,
      problemStatement,
    });
  } catch {
    return await apiRequest("/make-prediction", "POST", {
      domain,
      skillLevel,
      teammates: team.map((t) => t.name || t.email).join(", "),
      problemStatement,
    });
  }
}

// ---- CHATBOT ----
export async function aiChat({ prompt, systemPrompt }) {
  // Preferred: a server-proxied model (Gemini/OpenAI)
  try {
    const res = await apiRequest("/ai/chat", "POST", { prompt, systemPrompt });
    return res?.text || res?.message || "";
  } catch {
    // Fallback: your earlier /ai/gemini proxy
    const res = await apiRequest("/ai/gemini", "POST", {
      prompt,
      systemPrompt,
    });
    return res?.text || res?.message || "";
  }
}
