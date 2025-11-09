import React, { useState } from "react";
import bg from "../assets/Profilepicture.jpeg";
import { useNavigate } from "react-router-dom";
import { apiRequest } from "../api";
import { aiFormTeam, aiSelectProblemStatements, aiGeneratePlan } from "../ai";

export default function NewProjectFlow() {
  const navigate = useNavigate();

  const [flowStep, setFlowStep] = useState("choose_team");
  const [formData, setFormData] = useState({
    domain: "",
    teammatesRaw: "", // for manual input (emails/ids/names)
    skillLevel: "",
  });

  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Team formation results (AI)
  const [teamSuggestion, setTeamSuggestion] = useState({
    members: [],
    note: "",
  });

  // Problem statement (PS) selection
  const [psOptions, setPsOptions] = useState([]); // [{id,title,brief}]
  const [recommendedId, setRecommendedId] = useState(null);
  const [selectedPsId, setSelectedPsId] = useState(null);

  // Plan from AI
  const [aiPlan, setAiPlan] = useState(null);

  const validateForm = (withTeam) => {
    const n = {};
    if (!formData.domain) n.domain = "Required.";
    if (!formData.skillLevel) n.skillLevel = "Required.";
    if (withTeam && !formData.teammatesRaw.trim()) n.teammatesRaw = "Required.";
    setErrors(n);
    return Object.keys(n).length === 0;
  };

  // ---- STEPS ----

  // 1) Manual team → jump to PS selection
  const handleManualTeamSubmit = async () => {
    if (!validateForm(true)) return;
    setTeamSuggestion({
      members: formData.teammatesRaw
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean)
        .map((s) => ({ name: s })),
      note: "Manual team provided.",
    });
    await doPsSelection();
  };

  // 2) Need a team → AI forms team → then PS selection
  const handleMlTeamSubmit = async () => {
    if (!validateForm(false)) return;
    setLoading(true);
    setApiError(null);
    try {
      const out = await aiFormTeam({
        domain: formData.domain,
        skillLevel: formData.skillLevel,
        seedMembers: [], // you can pass the current user or seeds
      });
      // expected shape: { members: [{name,email,role,skills:[]}], note?: string }
      setTeamSuggestion({
        members: out?.members || [],
        note: out?.note || "",
      });
      await doPsSelection();
    } catch (err) {
      setApiError(err?.message || "Team formation failed.");
      setFlowStep("choose_team");
    } finally {
      setLoading(false);
    }
  };

  // 3) Get PS options from AI and move to PS selection step
  const doPsSelection = async () => {
    setLoading(true);
    setApiError(null);
    try {
      const res = await aiSelectProblemStatements({
        domain: formData.domain,
        skillLevel: formData.skillLevel,
        team: teamSuggestion.members,
      });
      // expected { options: [{id,title,brief}], recommendedId }
      setPsOptions(res?.options || []);
      setRecommendedId(res?.recommendedId || null);
      setSelectedPsId(res?.recommendedId || res?.options?.[0]?.id || null);
      setFlowStep("ps_selection");
    } catch (err) {
      setApiError(err?.message || "Problem statement selection failed.");
      setFlowStep("choose_team");
    } finally {
      setLoading(false);
    }
  };

  // 4) Generate plan based on chosen PS
  const handleGeneratePlan = async () => {
    if (!selectedPsId) {
      setApiError("Please choose a problem statement.");
      return;
    }
    const chosen = psOptions.find((p) => p.id === selectedPsId);
    setLoading(true);
    setApiError(null);
    try {
      const plan = await aiGeneratePlan({
        domain: formData.domain,
        skillLevel: formData.skillLevel,
        team: teamSuggestion.members,
        problemStatement: chosen?.title || chosen, // handle either shape
      });
      setAiPlan(plan);
      setFlowStep("display_plan");
    } catch (err) {
      setApiError(err?.message || "Plan generation failed.");
    } finally {
      setLoading(false);
    }
  };

  // 5) Save project
  const handleSaveProject = async () => {
    setLoading(true);
    setApiError(null);
    try {
      const saved = await apiRequest("/projects", "POST", {
        name: `${formData.domain} Project`,
        domain: formData.domain,
        skillLevel: formData.skillLevel,
        teammates: teamSuggestion.members,
        aiPlan,
        phase: "Phase 1 — Planning",
      });
      alert("Project created!");
      if (saved?.id) navigate(`/projects/${saved.id}`);
      else navigate("/projects");
    } catch (err) {
      setApiError(err?.message || "Saving project failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen bg-cover bg-center flex items-center justify-center"
      style={{ backgroundImage: `url(${bg})` }}
    >
      <div className="min-h-screen w-full bg-black/50 flex items-center justify-center p-6">
        <div className="bg-white/90 p-10 rounded-2xl shadow-lg w-full max-w-3xl">
          <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
            New Project Flow
          </h1>

          {apiError && (
            <div className="mb-4 p-3 bg-yellow-100 text-yellow-800 rounded">
              {apiError}
            </div>
          )}
          {loading && (
            <div className="mb-4 p-3 bg-blue-50 text-blue-800 rounded">
              Working... please wait.
            </div>
          )}

          {/* Step 0: Choose Team Mode */}
          {flowStep === "choose_team" && (
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-lg shadow-md">
                <label className="block mb-2 font-medium">Choose Domain</label>
                <select
                  value={formData.domain}
                  onChange={(e) =>
                    setFormData({ ...formData, domain: e.target.value })
                  }
                  className="w-full border p-2 rounded mb-1 bg-white"
                >
                  <option value="">Select Domain</option>
                  <option>Web Development</option>
                  <option>Artificial Intelligence</option>
                  <option>Machine Learning</option>
                  <option>Cybersecurity</option>
                  <option>Data Science</option>
                  <option>Mobile App Development</option>
                </select>
                {errors.domain && (
                  <p className="text-red-500 text-sm mb-3">{errors.domain}</p>
                )}

                <label className="block mb-2 font-medium">Skill Level</label>
                <select
                  value={formData.skillLevel}
                  onChange={(e) =>
                    setFormData({ ...formData, skillLevel: e.target.value })
                  }
                  className="w-full border p-2 rounded mb-1 bg-white"
                >
                  <option value="">Select</option>
                  <option>Beginner</option>
                  <option>Intermediate</option>
                  <option>Expert</option>
                </select>
                {errors.skillLevel && (
                  <p className="text-red-500 text-sm mb-3">
                    {errors.skillLevel}
                  </p>
                )}
              </div>

              <div className="flex justify-center gap-4">
                <button
                  onClick={() => setFlowStep("manual_team")}
                  className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition"
                >
                  I already have a team
                </button>
                <button
                  onClick={handleMlTeamSubmit}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
                >
                  I need a team (AI)
                </button>
              </div>
            </div>
          )}

          {/* Step 1: Manual team input */}
          {flowStep === "manual_team" && (
            <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-semibold mb-4">
                Add Teammates (comma-separated)
              </h2>
              <input
                type="text"
                value={formData.teammatesRaw}
                onChange={(e) =>
                  setFormData({ ...formData, teammatesRaw: e.target.value })
                }
                className="w-full border p-2 rounded mb-1"
                placeholder="names or emails, separated by commas"
              />
              {errors.teammatesRaw && (
                <p className="text-red-500 text-sm mb-2">
                  {errors.teammatesRaw}
                </p>
              )}

              <div className="flex justify-between mt-4">
                <button
                  onClick={() => setFlowStep("choose_team")}
                  className="bg-gray-400 text-white px-4 py-2 rounded"
                >
                  Back
                </button>
                <button
                  onClick={handleManualTeamSubmit}
                  className="bg-green-600 text-white px-6 py-2 rounded"
                >
                  Continue
                </button>
              </div>
            </div>
          )}

          {/* Step 2: PS selection */}
          {flowStep === "ps_selection" && (
            <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-semibold mb-3">
                Choose a Problem Statement
              </h2>
              {teamSuggestion?.members?.length > 0 && (
                <p className="text-sm text-gray-600 mb-2">
                  Team ({teamSuggestion.members.length}):{" "}
                  {teamSuggestion.members
                    .map((m) => m.name || m.email)
                    .filter(Boolean)
                    .join(", ")}
                </p>
              )}
              {teamSuggestion?.note && (
                <p className="text-xs text-gray-500 mb-3">
                  {teamSuggestion.note}
                </p>
              )}

              {psOptions.length === 0 ? (
                <p className="text-gray-600">No options returned by AI.</p>
              ) : (
                <div className="space-y-3">
                  {psOptions.map((opt) => (
                    <label
                      key={opt.id}
                      className="block border rounded p-3 hover:bg-gray-50 cursor-pointer"
                    >
                      <div className="flex items-start gap-3">
                        <input
                          type="radio"
                          name="ps"
                          checked={selectedPsId === opt.id}
                          onChange={() => setSelectedPsId(opt.id)}
                          className="mt-1"
                        />
                        <div>
                          <div className="font-semibold">
                            {opt.title}{" "}
                            {recommendedId === opt.id && (
                              <span className="ml-2 text-xs text-white bg-green-600 px-2 py-0.5 rounded">
                                Recommended
                              </span>
                            )}
                          </div>
                          {opt.brief && (
                            <p className="text-sm text-gray-600 mt-1">
                              {opt.brief}
                            </p>
                          )}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              )}

              <div className="flex justify-between mt-4">
                <button
                  onClick={() => setFlowStep("choose_team")}
                  className="bg-gray-400 text-white px-4 py-2 rounded"
                >
                  Start Over
                </button>
                <button
                  onClick={handleGeneratePlan}
                  className="bg-indigo-600 text-white px-6 py-2 rounded"
                >
                  Generate Plan
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Display plan */}
          {flowStep === "display_plan" && aiPlan && (
            <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-semibold mb-4">AI Project Plan</h2>

              {aiPlan.problemStatement && (
                <div className="mb-3">
                  <h3 className="font-semibold">Problem Statement</h3>
                  <p>{aiPlan.problemStatement}</p>
                </div>
              )}

              {aiPlan.details && (
                <div className="mb-3">
                  <h3 className="font-semibold">Details</h3>
                  <p className="whitespace-pre-wrap">{aiPlan.details}</p>
                </div>
              )}

              {aiPlan.taskDetails && (
                <div className="mb-3">
                  <h3 className="font-semibold">Task Breakdown</h3>
                  <pre className="bg-gray-100 p-2 rounded text-sm whitespace-pre-wrap">
                    {aiPlan.taskDetails}
                  </pre>
                </div>
              )}

              <div className="flex justify-between mt-4">
                <button
                  onClick={() => setFlowStep("ps_selection")}
                  className="bg-gray-400 text-white px-4 py-2 rounded"
                >
                  Back
                </button>
                <button
                  onClick={handleSaveProject}
                  className="bg-green-600 text-white px-6 py-2 rounded"
                >
                  Save Project
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
