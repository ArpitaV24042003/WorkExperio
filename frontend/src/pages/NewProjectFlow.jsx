import React, { useState } from "react";
import bg from "../assets/Profilepicture.jpeg"; // ✅ same background image
import { apiRequest } from "../api"; // <- make sure src/api.js exists and is exported

export default function NewProjectFlow() {
  const [flowStep, setFlowStep] = useState("choose_team");
  const [formData, setFormData] = useState({
    domain: "",
    teammates: "",
    skillLevel: "",
  });
  const [errors, setErrors] = useState({});
  const [waitingList, setWaitingList] = useState([]);
  const [llmResponse, setLlmResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState(null);

  // Dummy fallback response used when the backend/DB is unavailable
  const dummyResponse = {
    problemStatement: "Develop a decentralized social media platform.",
    details: "A detailed breakdown of the problem... (fallback)",
    taskDetails:
      "- Task 1: Design the UI\n- Task 2: Build API\n- Task 3: Integrate AI module\n(These are mock tasks returned when backend is unreachable.)",
  };

  const validateForm = (isExistingTeam) => {
    let newErrors = {};

    if (!formData.domain.trim()) {
      newErrors.domain = "Filling this field is Required.";
    }

    if (isExistingTeam && !formData.teammates.trim()) {
      newErrors.teammates = "Filling this field is Required.";
    }

    if (!isExistingTeam && !formData.skillLevel.trim()) {
      newErrors.skillLevel = "Filling this field is Required.";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleManualTeamSubmit = () => {
    if (!validateForm(true)) return;
    // Save minimal info locally or let backend save later
    setFlowStep("llm_process");
  };

  const handleMlTeamSubmit = () => {
    if (!validateForm(false)) return;
    setWaitingList((prev) => [...prev, { id: Date.now(), ...formData }]);
    setFlowStep("waiting_list");
  };

  const handleTeamFormed = () => setFlowStep("llm_process");

  // Calls the backend LLM proxy at /make-prediction
  // If the backend fails, fallback to dummyResponse so UI can continue.
  const handleLlmSubmit = async () => {
    setLoading(true);
    setApiError(null);

    // Build the payload expected by your backend/ML model.
    // Adjust keys to match the backend contract.
    const payload = {
      domain: formData.domain,
      teammates: formData.teammates,
      skillLevel: formData.skillLevel,
      // you can include more context here
    };

    try {
      // Try calling the backend proxy endpoint
      const response = await apiRequest("/make-prediction", "POST", payload);
      // response should be the model output. Adjust if backend wraps data differently.
      setLlmResponse(response);
      setFlowStep("display_llm_response");
    } catch (err) {
      console.warn("LLM call failed, using fallback dummy response:", err);
      setApiError(
        "Unable to reach LLM backend. Using fallback data so you can continue testing."
      );
      // fallback so frontend testing can continue
      setLlmResponse(dummyResponse);
      setFlowStep("display_llm_response");
    } finally {
      setLoading(false);
    }
  };

  // Try to save the project to backend at /projects (or whatever your endpoint)
  // If DB is down, show error and let user continue locally
  const handleSaveToDatabase = async () => {
    setLoading(true);
    setApiError(null);

    const projectPayload = {
      domain: formData.domain,
      teammates:
        formData.teammates
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean) || [],
      skillLevel: formData.skillLevel,
      llmGenerated: llmResponse,
      createdAt: new Date().toISOString(),
    };

    try {
      // IMPORTANT: change "/projects" to your real create-project endpoint if different
      const saved = await apiRequest("/projects", "POST", projectPayload);
      alert("Project details saved to the database successfully!");
      // Reset
      setFlowStep("choose_team");
      setFormData({ domain: "", teammates: "", skillLevel: "" });
      setErrors({});
      setLlmResponse(null);
      // Optionally update UI with saved project if response contains it
      console.log("Saved project response:", saved);
    } catch (err) {
      console.error("Failed to save project:", err);
      setApiError(
        "Saving to DB failed (likely Postgres). Your project is still shown locally."
      );
      // Keep the LLM response and allow user to continue; you can also persist locally as needed
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen bg-cover bg-center flex items-center justify-center"
      style={{ backgroundImage: `url(${bg})` }}
    >
      {/* Overlay */}
      <div className="min-h-screen w-full bg-black bg-opacity-50 flex items-center justify-center p-6">
        <div className="bg-white bg-opacity-90 p-10 rounded-2xl shadow-lg w-full max-w-3xl">
          <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
            New Project Flow (Team Formation)
          </h1>

          {/* Global status / errors */}
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

          {/* Step 1: Choose Team */}
          {flowStep === "choose_team" && (
            <div className="space-x-6 flex justify-center">
              <button
                onClick={() => setFlowStep("manual_team")}
                className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition"
              >
                I already have a team
              </button>
              <button
                onClick={() => setFlowStep("ml_team")}
                className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition"
              >
                I need a team
              </button>
            </div>
          )}

          {/* Step 2a: Manual Team Form */}
          {flowStep === "manual_team" && (
            <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-semibold mb-4">
                Create New Project (With Existing Team)
              </h2>

              <label className="block mb-2 font-medium">Choose Domain</label>
              <select
                value={formData.domain}
                onChange={(e) =>
                  setFormData({ ...formData, domain: e.target.value })
                }
                className="w-full border p-2 rounded mb-1 bg-white"
              >
                <option value="">Select Domain</option>
                <option value="Web Development">Web Development</option>
                <option value="Artificial Intelligence">Artificial Intelligence</option>
                <option value="Machine Learning">Machine Learning</option>
                <option value="Cybersecurity">Cybersecurity</option>
                <option value="Data Science">Data Science</option>
                <option value="Mobile App Development">Mobile App Development</option>
              </select>
              {errors.domain && (
                <p className="text-red-500 text-sm mb-3">{errors.domain}</p>
              )}

              <label className="block mb-2 font-medium">
                Add Teammates (WorkExperio User IDs)
              </label>
              <input
                type="text"
                value={formData.teammates}
                onChange={(e) =>
                  setFormData({ ...formData, teammates: e.target.value })
                }
                className="w-full border p-2 rounded mb-1"
                placeholder="Comma-separated IDs"
              />
              {errors.teammates && (
                <p className="text-red-500 text-sm mb-3">{errors.teammates}</p>
              )}

              <label className="block mb-2 font-medium">
                Analyze Skill Level (optional)
              </label>
              <select
                value={formData.skillLevel}
                onChange={(e) =>
                  setFormData({ ...formData, skillLevel: e.target.value })
                }
                className="w-full border p-2 rounded mb-3 bg-white"
              >
                <option value="">Select Skill Level</option>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Expert">Expert</option>
              </select>

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
                  Submit
                </button>
              </div>
            </div>
          )}

          {/* Step 2b: ML Team Form */}
          {flowStep === "ml_team" && (
            <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-semibold mb-4">
                Create New Project (Find Team)
              </h2>

              <label className="block mb-2 font-medium">Choose Domain</label>
              <select
                value={formData.domain}
                onChange={(e) =>
                  setFormData({ ...formData, domain: e.target.value })
                }
                className="w-full border p-2 rounded mb-1 bg-white"
              >
                <option value="">Select Domain</option>
                <option value="Web Development">Web Development</option>
                <option value="Artificial Intelligence">Artificial Intelligence</option>
                <option value="Machine Learning">Machine Learning</option>
                <option value="Cybersecurity">Cybersecurity</option>
                <option value="Data Science">Data Science</option>
                <option value="Mobile App Development">Mobile App Development</option>
              </select>
              {errors.domain && (
                <p className="text-red-500 text-sm mb-3">{errors.domain}</p>
              )}

              <label className="block mb-2 font-medium">Analyze Skill Level</label>
              <select
                value={formData.skillLevel}
                onChange={(e) =>
                  setFormData({ ...formData, skillLevel: e.target.value })
                }
                className="w-full border p-2 rounded mb-3 bg-white"
              >
                <option value="">Select Skill Level</option>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Expert">Expert</option>
              </select>
              {errors.skillLevel && (
                <p className="text-red-500 text-sm mb-3">{errors.skillLevel}</p>
              )}

              <div className="flex justify-between mt-4">
                <button
                  onClick={() => setFlowStep("choose_team")}
                  className="bg-gray-400 text-white px-4 py-2 rounded"
                >
                  Back
                </button>
                <button
                  onClick={handleMlTeamSubmit}
                  className="bg-green-600 text-white px-6 py-2 rounded"
                >
                  Submit
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Waiting List */}
          {flowStep === "waiting_list" && (
            <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-semibold mb-4">Team Formation in Progress</h2>
              <p>
                You've been added to the waiting list. The ML algorithm is
                forming your team based on project requirements and skill
                levels.
              </p>
              <div className="flex justify-center mt-4">
                <button
                  onClick={handleTeamFormed}
                  className="bg-purple-600 text-white px-6 py-2 rounded"
                >
                  Simulate Team Formed
                </button>
              </div>
            </div>
          )}

          {/* Step 4: LLM Process */}
          {flowStep === "llm_process" && (
            <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-semibold mb-4">
                Generating Project Details with LLM
              </h2>
              <p>Please wait while the Large Language Model generates the detailed project plan.</p>
              <div className="flex justify-center mt-4">
                <button
                  onClick={handleLlmSubmit}
                  className="bg-cyan-600 text-white px-6 py-2 rounded"
                  disabled={loading}
                >
                  {loading ? "Running..." : "Run LLM Model"}
                </button>
              </div>
            </div>
          )}

          {/* Step 5: Display LLM Response */}
          {flowStep === "display_llm_response" && llmResponse && (
            <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-semibold mb-4">LLM Generated Project Plan</h2>

              <div className="mb-4">
                <h3 className="font-semibold">Problem Statement:</h3>
                <p>{llmResponse.problemStatement}</p>
              </div>

              <div className="mb-4">
                <h3 className="font-semibold">Details:</h3>
                <p>{llmResponse.details}</p>
              </div>

              <div className="mb-4">
                <h3 className="font-semibold">Task Breakdown:</h3>
                <pre className="bg-gray-100 p-2 rounded text-sm whitespace-pre-wrap">
                  {llmResponse.taskDetails}
                </pre>
              </div>

              <div className="flex justify-between mt-4">
                <button
                  onClick={() => setFlowStep("llm_process")}
                  className="bg-gray-400 text-white px-4 py-2 rounded"
                >
                  Regenerate
                </button>
                <div className="flex gap-3">
                  <button
                    onClick={handleSaveToDatabase}
                    className="bg-green-600 text-white px-6 py-2 rounded"
                    disabled={loading}
                  >
                    {loading ? "Saving..." : "Save to Database"}
                  </button>
                  <button
                    onClick={() => {
                      // locally dismiss and reset state without saving
                      setFlowStep("choose_team");
                      setFormData({ domain: "", teammates: "", skillLevel: "" });
                      setLlmResponse(null);
                      setErrors({});
                    }}
                    className="bg-gray-200 text-gray-800 px-4 py-2 rounded"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
