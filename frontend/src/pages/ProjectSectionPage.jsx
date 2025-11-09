// import React, { useState } from "react";
// import bg from "../assets/Profilepicture.jpeg";
// import { apiRequest } from "../api";

// export default function ProjectSection() {
//   // ✅ For new users, start empty. For testing, preloaded one project.
//   const [projects, setProjects] = useState([
//     {
//       name: "AI-Powered Career Guidance",
//       domain: "Machine Learning",
//       skillLevel: "Intermediate",
//       description:
//         "A web platform that analyzes student resumes using AI/ML to extract skills and recommend personalized career paths.",
//       team: ["Alice (PM)", "Bob (Backend)", "Charlie (Frontend)", "Diana (Data Scientist)"],
//       phase: "Phase 3 — Development in Progress",
//     },
//   ]);

//   const [showOverlay, setShowOverlay] = useState(false);
//   const [selectedProject, setSelectedProject] = useState(null);
//   const [newProject, setNewProject] = useState({
//     domain: "",
//     skillLevel: "",
//   });

//   const handleAddProject = () => {
//     if (newProject.domain && newProject.skillLevel) {
//       const project = {
//         name: newProject.domain,
//         domain: newProject.domain,
//         skillLevel: newProject.skillLevel,
//         description: "New project added by user.",
//         team: ["Not assigned"],
//         phase: "Phase 1 — Planning",
//       };
//       setProjects([...projects, project]);
//       setShowOverlay(false);
//       setNewProject({ domain: "", skillLevel: "" });
//     } else {
//       alert("Please fill in all fields.");
//     }
//   };

//   const handleProjectClick = (project) => {
//     setSelectedProject(project);
//   };

//   const closeProjectDetails = () => {
//     setSelectedProject(null);
//   };

//   return (
//     <div
//       className="min-h-screen bg-cover bg-center flex items-center justify-center p-6"
//       style={{ backgroundImage: `url(${bg})` }}
//     >
//       <div className="w-full max-w-md bg-white/90 backdrop-blur-md shadow-xl rounded-2xl p-6 border border-gray-200">
//         <h2 className="text-2xl font-bold mb-6 text-gray-800 text-center">
//           Project Section
//         </h2>

//         {/* Project List */}
//         {projects.length === 0 ? (
//           <p className="text-gray-600 italic text-center">
//             No projects yet. Add one to get started!
//           </p>
//         ) : (
//           <ul className="space-y-3 mb-6">
//             {projects.map((project, index) => (
//               <li
//                 key={index}
//                 onClick={() => handleProjectClick(project)}
//                 className="bg-teal-200 text-gray-800 p-3 rounded-md shadow-sm text-center cursor-pointer hover:bg-teal-300 transition"
//               >
//                 {project.name}
//               </li>
//             ))}
//           </ul>
//         )}

//         {/* New Project Button */}
//         <button
//           onClick={() => setShowOverlay(true)}
//           className="w-full bg-red-400 hover:bg-red-500 text-white p-2 rounded-md font-semibold transition-all duration-200"
//         >
//           New Project
//         </button>
//       </div>

//       {/* Overlay for New Project */}
//       {showOverlay && (
//         <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
//           <div className="bg-white/95 backdrop-blur-md w-full max-w-md p-6 rounded-2xl shadow-2xl border border-gray-200">
//             <h3 className="text-lg font-bold mb-4 text-gray-800 text-center">
//               New Project
//             </h3>

//             {/* Domain Dropdown */}
//             <label className="block mb-2 font-medium text-gray-700">
//               Choose Domain
//             </label>
//             <select
//               value={newProject.domain}
//               onChange={(e) =>
//                 setNewProject({ ...newProject, domain: e.target.value })
//               }
//               required
//               className="w-full border border-gray-300 p-2 rounded mb-4 bg-white"
//             >
//               <option value="">Select a domain</option>
//               <option value="Web Development">Web Development</option>
//               <option value="Machine Learning">Machine Learning</option>
//               <option value="Data Analytics">Data Analytics</option>
//               <option value="IoT">IoT</option>
//               <option value="Cybersecurity">Cybersecurity</option>
//             </select>

//             {/* Skill Level Dropdown */}
//             <label className="block mb-2 font-medium text-gray-700">
//               Skill Level
//             </label>
//             <select
//               value={newProject.skillLevel}
//               onChange={(e) =>
//                 setNewProject({ ...newProject, skillLevel: e.target.value })
//               }
//               required
//               className="w-full border border-gray-300 p-2 rounded mb-6 bg-white"
//             >
//               <option value="">Select your skill level</option>
//               <option value="Beginner">Beginner</option>
//               <option value="Intermediate">Intermediate</option>
//               <option value="Advanced">Advanced</option>
//             </select>

//             {/* Buttons */}
//             <div className="flex justify-end space-x-3">
//               <button
//                 onClick={() => setShowOverlay(false)}
//                 className="bg-gray-300 hover:bg-gray-400 px-4 py-2 rounded-md transition-all"
//               >
//                 Cancel
//               </button>
//               <button
//                 onClick={handleAddProject}
//                 className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-all"
//               >
//                 Submit
//               </button>
//             </div>
//           </div>
//         </div>
//       )}

//       {/* Project Details Modal */}
//       {selectedProject && (
//         <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
//           <div className="bg-white w-full max-w-lg rounded-2xl shadow-2xl p-6 relative">
//             <h3 className="text-xl font-bold mb-3 text-gray-800">
//               {selectedProject.name}
//             </h3>
//             <p className="text-gray-700 mb-3">
//               <strong>Domain:</strong> {selectedProject.domain}
//             </p>
//             <p className="text-gray-700 mb-3">
//               <strong>Skill Level:</strong> {selectedProject.skillLevel}
//             </p>
//             <p className="text-gray-700 mb-3">
//               <strong>Description:</strong> {selectedProject.description}
//             </p>
//             <p className="text-gray-700 mb-3">
//               <strong>Team:</strong> {selectedProject.team.join(", ")}
//             </p>
//             <p className="text-gray-700 mb-5">
//               <strong>Current Phase:</strong> {selectedProject.phase}
//             </p>
//             <div className="flex justify-end">
//               <button
//                 onClick={closeProjectDetails}
//                 className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-all"
//               >
//                 Close
//               </button>
//             </div>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// }

import React, { useEffect, useState } from "react";
import bg from "../assets/Profilepicture.jpeg";
import { apiRequest } from "../api";
import { useNavigate } from "react-router-dom";

export default function ProjectSection() {
  const navigate = useNavigate();

  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState(null);

  const [showOverlay, setShowOverlay] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [creating, setCreating] = useState(false);

  const [newProject, setNewProject] = useState({
    domain: "",
    skillLevel: "",
  });

  // Fetch all projects on mount
  useEffect(() => {
    let ignore = false;
    (async () => {
      setLoading(true);
      setApiError(null);
      try {
        const list = await apiRequest("/projects", "GET");
        if (!ignore) setProjects(Array.isArray(list) ? list : []);
      } catch (err) {
        if (!ignore) setApiError(err?.message || "Failed to load projects");
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    return () => (ignore = true);
  }, []);

  const handleAddProject = async () => {
    if (!newProject.domain || !newProject.skillLevel) {
      alert("Please fill in all fields.");
      return;
    }

    setCreating(true);
    setApiError(null);

    const payload = {
      name: `${newProject.domain} Project`,
      domain: newProject.domain,
      skillLevel: newProject.skillLevel,
      description: "New project created from Project Section.",
      team: [],
      phase: "Phase 1 — Planning",
      createdAt: new Date().toISOString(),
    };

    try {
      // Expecting: { id, ...project }
      const saved = await apiRequest("/projects", "POST", payload);
      setProjects((prev) => [saved, ...prev]);
      setShowOverlay(false);
      setNewProject({ domain: "", skillLevel: "" });
    } catch (err) {
      setApiError(err?.message || "Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  const handleProjectClick = (project) => setSelectedProject(project);
  const closeProjectDetails = () => setSelectedProject(null);

  return (
    <div
      className="min-h-screen bg-cover bg-center flex items-center justify-center p-6"
      style={{ backgroundImage: `url(${bg})` }}
    >
      <div className="w-full max-w-md bg-white/90 backdrop-blur-md shadow-xl rounded-2xl p-6 border border-gray-200">
        <h2 className="text-2xl font-bold mb-6 text-gray-800 text-center">
          Project Section
        </h2>

        {apiError && (
          <div className="mb-4 p-3 bg-yellow-100 text-yellow-800 rounded">
            {apiError}
          </div>
        )}

        {loading ? (
          <p className="text-gray-600 italic text-center">Loading projects…</p>
        ) : projects.length === 0 ? (
          <p className="text-gray-600 italic text-center">
            No projects yet. Add one to get started!
          </p>
        ) : (
          <ul className="space-y-3 mb-6">
            {projects.map((project) => (
              <li
                key={project.id}
                onClick={() => handleProjectClick(project)}
                className="bg-teal-200 text-gray-800 p-3 rounded-md shadow-sm text-center cursor-pointer hover:bg-teal-300 transition"
              >
                {project.name}
              </li>
            ))}
          </ul>
        )}

        <button
          onClick={() => setShowOverlay(true)}
          className="w-full bg-red-400 hover:bg-red-500 text-white p-2 rounded-md font-semibold transition-all duration-200"
        >
          New Project
        </button>
      </div>

      {/* Create Project Overlay */}
      {showOverlay && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white/95 backdrop-blur-md w-full max-w-md p-6 rounded-2xl shadow-2xl border border-gray-200">
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

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowOverlay(false)}
                className="bg-gray-300 hover:bg-gray-400 px-4 py-2 rounded-md transition-all"
                disabled={creating}
              >
                Cancel
              </button>
              <button
                onClick={handleAddProject}
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-all"
                disabled={creating}
              >
                {creating ? "Creating…" : "Submit"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Project Details Modal */}
      {selectedProject && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
          <div className="bg-white w-full max-w-lg rounded-2xl shadow-2xl p-6 relative">
            <h3 className="text-xl font-bold mb-3 text-gray-800">
              {selectedProject.name}
            </h3>
            <p className="text-gray-700 mb-3">
              <strong>Domain:</strong> {selectedProject.domain}
            </p>
            <p className="text-gray-700 mb-3">
              <strong>Skill Level:</strong> {selectedProject.skillLevel}
            </p>
            {selectedProject.description && (
              <p className="text-gray-700 mb-3">
                <strong>Description:</strong> {selectedProject.description}
              </p>
            )}
            {selectedProject.team?.length ? (
              <p className="text-gray-700 mb-3">
                <strong>Team:</strong> {selectedProject.team.join(", ")}
              </p>
            ) : null}
            {selectedProject.phase && (
              <p className="text-gray-700 mb-5">
                <strong>Current Phase:</strong> {selectedProject.phase}
              </p>
            )}

            <div className="flex justify-between">
              <button
                onClick={closeProjectDetails}
                className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-md transition-all"
              >
                Close
              </button>
              <button
                onClick={() => navigate(`/projects/${selectedProject.id}`)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-all"
              >
                Open Project
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
