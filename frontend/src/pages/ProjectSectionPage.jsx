import React, { useEffect, useState } from "react";
import bg from "../assets/Profilepicture.jpeg";
import { apiRequest } from "../api";
import { useNavigate } from "react-router-dom";

export default function ProjectSectionPage() {
  const navigate = useNavigate();

  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState(null);

  const [showOverlay, setShowOverlay] = useState(false);
  const [newProject, setNewProject] = useState({ domain: "", skillLevel: "" });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    let ignore = false;
    (async () => {
      setLoading(true);
      setApiError(null);
      try {
        const data = await apiRequest("/projects?mine=true");
        if (!ignore) setProjects(Array.isArray(data) ? data : []);
      } catch (e) {
        if (!ignore) setApiError(e?.message || "Failed to load projects");
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    return () => (ignore = true);
  }, []);

  const handleAddProject = async () => {
    if (!newProject.domain || !newProject.skillLevel) {
      alert("Please choose both domain and skill level.");
      return;
    }

    setCreating(true);
    setApiError(null);

    try {
      // 1) Ask AI to generate plan
      const aiPlan = await apiRequest("/make-prediction", "POST", {
        domain: newProject.domain,
        skillLevel: newProject.skillLevel,
        teammates: [],
      });

      // 2) Save project to DB
      const saved = await apiRequest("/projects", "POST", {
        name: `${newProject.domain} Project`,
        domain: newProject.domain,
        skillLevel: newProject.skillLevel,
        teammates: [],
        aiPlan,
        phase: "Phase 1 — Planning",
      });

      // 3) Navigate to its page
      if (saved?.id) {
        navigate(`/projects/${saved.id}`);
      } else {
        // refresh list and close
        const list = await apiRequest("/projects?mine=true");
        setProjects(Array.isArray(list) ? list : []);
        setShowOverlay(false);
      }
    } catch (e) {
      setApiError(e?.message || "Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  const openProject = (p) => navigate(`/projects/${p.id}`);

  return (
    <div
      className="min-h-screen bg-cover bg-center flex items-center justify-center p-6"
      style={{ backgroundImage: `url(${bg})` }}
    >
      <div className="w-full max-w-xl bg-white/90 backdrop-blur-md shadow-xl rounded-2xl p-6 border border-gray-200">
        <h2 className="text-2xl font-bold mb-6 text-gray-800 text-center">
          Project Section
        </h2>

        {apiError && (
          <div className="mb-4 p-3 bg-yellow-100 text-yellow-800 rounded">
            {apiError}
          </div>
        )}

        {/* Project List */}
        {loading ? (
          <p className="text-gray-600 italic text-center">Loading projects…</p>
        ) : projects.length === 0 ? (
          <p className="text-gray-600 italic text-center">
            No projects yet. Click “New Project” to start!
          </p>
        ) : (
          <ul className="space-y-3 mb-6">
            {projects.map((project) => (
              <li
                key={project.id}
                onClick={() => openProject(project)}
                className="bg-teal-200 text-gray-800 p-3 rounded-md shadow-sm text-center cursor-pointer hover:bg-teal-300 transition"
              >
                {project.name}
              </li>
            ))}
          </ul>
        )}

        {/* New Project Button */}
        <button
          onClick={() => setShowOverlay(true)}
          className="w-full bg-red-500 hover:bg-red-600 text-white p-2 rounded-md font-semibold transition-all duration-200"
        >
          New Project
        </button>
      </div>

      {/* Overlay */}
      {showOverlay && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-white w-full max-w-md p-6 rounded-2xl shadow-2xl border border-gray-200">
            <h3 className="text-lg font-bold mb-4 text-gray-800 text-center">
              New Project
            </h3>

            <label className="block mb-2 font-medium text-gray-700">
              Choose Domain
            </label>
            <select
              value={newProject.domain}
              onChange={(e) =>
                setNewProject({ ...newProject, domain: e.target.value })
              }
              required
              className="w-full border border-gray-300 p-2 rounded mb-4 bg-white"
            >
              <option value="">Select a domain</option>
              <option value="Web Development">Web Development</option>
              <option value="Machine Learning">Machine Learning</option>
              <option value="Data Analytics">Data Analytics</option>
              <option value="IoT">IoT</option>
              <option value="Cybersecurity">Cybersecurity</option>
            </select>

            <label className="block mb-2 font-medium text-gray-700">
              Skill Level
            </label>
            <select
              value={newProject.skillLevel}
              onChange={(e) =>
                setNewProject({ ...newProject, skillLevel: e.target.value })
              }
              required
              className="w-full border border-gray-300 p-2 rounded mb-6 bg-white"
            >
              <option value="">Select your skill level</option>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowOverlay(false)}
                className="bg-gray-300 hover:bg-gray-400 px-4 py-2 rounded-md transition-all"
                disabled={creating}
              >
                Cancel
              </button>
              <button
                onClick={handleAddProject}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition-all"
                disabled={creating}
              >
                {creating ? "Creating…" : "Create"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
