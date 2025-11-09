// import React, { useEffect, useState } from "react";
// import { useParams, Link } from "react-router-dom";
// import { apiRequest } from "../api";

// export default function ProjectHomePage() {
//   const { id } = useParams();
//   const [project, setProject] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [saving, setSaving] = useState(false);
//   const [planning, setPlanning] = useState(false);
//   const [apiError, setApiError] = useState(null);

//   // editable fields
//   const [form, setForm] = useState({
//     name: "",
//     domain: "",
//     skillLevel: "",
//     description: "",
//   });

//   useEffect(() => {
//     let ignore = false;
//     (async () => {
//       setLoading(true);
//       setApiError(null);
//       try {
//         const data = await apiRequest(`/projects/${id}`, "GET");
//         if (!ignore) {
//           setProject(data);
//           setForm({
//             name: data.name || "",
//             domain: data.domain || "",
//             skillLevel: data.skillLevel || "",
//             description: data.description || "",
//           });
//         }
//       } catch (err) {
//         if (!ignore) setApiError(err?.message || "Failed to load project");
//       } finally {
//         if (!ignore) setLoading(false);
//       }
//     })();
//     return () => (ignore = true);
//   }, [id]);

//   const saveBasics = async () => {
//     setSaving(true);
//     setApiError(null);
//     try {
//       const updated = await apiRequest(`/projects/${id}`, "PATCH", form);
//       setProject(updated);
//     } catch (err) {
//       setApiError(err?.message || "Save failed");
//     } finally {
//       setSaving(false);
//     }
//   };

//   const generatePlan = async () => {
//     setPlanning(true);
//     setApiError(null);
//     try {
//       // Backend should call your LLM (Gemini/OpenAI) and persist the result into the project
//       // and return the updated project with .aiPlan (problemStatement/details/tasks)
//       const updated = await apiRequest(`/projects/${id}/plan`, "POST", {
//         // you may pass additional context; backend can also read from DB
//         domain: project?.domain,
//         skillLevel: project?.skillLevel,
//         teammates: project?.team || [],
//       });
//       setProject(updated);
//     } catch (err) {
//       setApiError(err?.message || "Plan generation failed");
//     } finally {
//       setPlanning(false);
//     }
//   };

//   if (loading) {
//     return <div className="p-6">Loading…</div>;
//   }

//   if (!project) {
//     return (
//       <div className="p-6">
//         <p className="text-red-600 mb-4">{apiError || "Project not found."}</p>
//         <Link className="text-blue-600 underline" to="/projects">
//           Back to Projects
//         </Link>
//       </div>
//     );
//   }

//   const ai = project.aiPlan || project.llmGenerated; // support both keys

//   return (
//     <div className="p-6 max-w-4xl mx-auto">
//       <div className="flex items-center justify-between mb-4">
//         <h1 className="text-2xl font-bold">{project.name}</h1>
//         <Link to="/projects" className="text-blue-600 underline">
//           Back to Projects
//         </Link>
//       </div>

//       {apiError && (
//         <div className="mb-4 p-3 bg-yellow-100 text-yellow-800 rounded">
//           {apiError}
//         </div>
//       )}

//       <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//         {/* Basics */}
//         <div className="bg-white rounded-xl shadow p-4">
//           <h2 className="font-semibold mb-3">Basics</h2>

//           <label className="block text-sm font-medium">Name</label>
//           <input
//             className="border p-2 rounded w-full mb-3"
//             value={form.name}
//             onChange={(e) => setForm({ ...form, name: e.target.value })}
//           />

//           <label className="block text-sm font-medium">Domain</label>
//           <input
//             className="border p-2 rounded w-full mb-3"
//             value={form.domain}
//             onChange={(e) => setForm({ ...form, domain: e.target.value })}
//           />

//           <label className="block text-sm font-medium">Skill Level</label>
//           <select
//             className="border p-2 rounded w-full mb-3 bg-white"
//             value={form.skillLevel}
//             onChange={(e) => setForm({ ...form, skillLevel: e.target.value })}
//           >
//             <option value="">Select</option>
//             <option>Beginner</option>
//             <option>Intermediate</option>
//             <option>Advanced</option>
//           </select>

//           <label className="block text-sm font-medium">Description</label>
//           <textarea
//             className="border p-2 rounded w-full mb-4"
//             rows={4}
//             value={form.description}
//             onChange={(e) => setForm({ ...form, description: e.target.value })}
//           />

//           <button
//             onClick={saveBasics}
//             disabled={saving}
//             className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
//           >
//             {saving ? "Saving…" : "Save"}
//           </button>
//         </div>

//         {/* AI Plan */}
//         <div className="bg-white rounded-xl shadow p-4">
//           <div className="flex items-center justify-between mb-3">
//             <h2 className="font-semibold">AI Project Plan</h2>
//             <button
//               onClick={generatePlan}
//               disabled={planning}
//               className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded"
//             >
//               {planning
//                 ? "Generating…"
//                 : ai
//                 ? "Regenerate Plan"
//                 : "Generate Plan"}
//             </button>
//           </div>

//           {!ai ? (
//             <p className="text-gray-600">No plan generated yet.</p>
//           ) : (
//             <div className="space-y-3">
//               {ai.problemStatement && (
//                 <div>
//                   <h3 className="font-semibold">Problem Statement</h3>
//                   <p className="text-gray-800">{ai.problemStatement}</p>
//                 </div>
//               )}
//               {ai.details && (
//                 <div>
//                   <h3 className="font-semibold">Details</h3>
//                   <p className="text-gray-800 whitespace-pre-wrap">
//                     {ai.details}
//                   </p>
//                 </div>
//               )}
//               {ai.taskDetails && (
//                 <div>
//                   <h3 className="font-semibold">Task Breakdown</h3>
//                   <pre className="bg-gray-100 p-2 rounded text-sm whitespace-pre-wrap">
//                     {ai.taskDetails}
//                   </pre>
//                 </div>
//               )}
//             </div>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { apiRequest } from "../api";

export default function ProjectHomePage() {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [planning, setPlanning] = useState(false);
  const [apiError, setApiError] = useState(null);

  const [form, setForm] = useState({
    name: "",
    domain: "",
    skillLevel: "",
    description: "",
  });

  useEffect(() => {
    let ignore = false;
    (async () => {
      setLoading(true);
      setApiError(null);
      try {
        const data = await apiRequest(`/projects/${id}`, "GET");
        if (!ignore && data) {
          setProject(data);
          setForm({
            name: data.name || "",
            domain: data.domain || "",
            skillLevel: data.skillLevel || "",
            description: data.description || "",
          });
        }
      } catch (err) {
        if (!ignore) setApiError(err?.message || "Failed to load project");
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    return () => (ignore = true);
  }, [id]);

  const saveBasics = async () => {
    setSaving(true);
    setApiError(null);
    try {
      const updated = await apiRequest(`/projects/${id}`, "PATCH", form);
      setProject(updated);
    } catch (err) {
      setApiError(err?.message || "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const generatePlan = async () => {
    setPlanning(true);
    setApiError(null);
    try {
      const updated = await apiRequest(`/projects/${id}/plan`, "POST", {
        domain: project?.domain,
        skillLevel: project?.skillLevel,
        teammates: project?.team || [],
      });
      setProject(updated);
    } catch (err) {
      setApiError(err?.message || "Plan generation failed");
    } finally {
      setPlanning(false);
    }
  };

  if (loading) return <div className="p-6">Loading…</div>;
  if (!project) {
    return (
      <div className="p-6">
        <p className="text-red-600 mb-4">{apiError || "Project not found."}</p>
        <Link className="text-blue-600 underline" to="/projects">
          Back to Projects
        </Link>
      </div>
    );
  }

  const ai = project.aiPlan || project.llmGenerated;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">{project.name}</h1>
        <Link to="/projects" className="text-blue-600 underline">
          Back to Projects
        </Link>
      </div>

      {apiError && (
        <div className="mb-4 p-3 bg-yellow-100 text-yellow-800 rounded">
          {apiError}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Basics */}
        <div className="bg-white rounded-xl shadow p-4">
          <h2 className="font-semibold mb-3">Basics</h2>

          <label className="block text-sm font-medium">Name</label>
          <input
            className="border p-2 rounded w-full mb-3"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />

          <label className="block text-sm font-medium">Domain</label>
          <input
            className="border p-2 rounded w-full mb-3"
            value={form.domain}
            onChange={(e) => setForm({ ...form, domain: e.target.value })}
          />

          <label className="block text-sm font-medium">Skill Level</label>
          <select
            className="border p-2 rounded w-full mb-3 bg-white"
            value={form.skillLevel}
            onChange={(e) => setForm({ ...form, skillLevel: e.target.value })}
          >
            <option value="">Select</option>
            <option>Beginner</option>
            <option>Intermediate</option>
            <option>Advanced</option>
          </select>

          <label className="block text-sm font-medium">Description</label>
          <textarea
            className="border p-2 rounded w-full mb-4"
            rows={4}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />

          <button
            onClick={saveBasics}
            disabled={saving}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
          >
            {saving ? "Saving…" : "Save"}
          </button>
        </div>

        {/* AI Plan */}
        <div className="bg-white rounded-xl shadow p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold">AI Project Plan</h2>
            <button
              onClick={generatePlan}
              disabled={planning}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded"
            >
              {planning
                ? "Generating…"
                : ai
                ? "Regenerate Plan"
                : "Generate Plan"}
            </button>
          </div>

          {!ai ? (
            <p className="text-gray-600">No plan generated yet.</p>
          ) : (
            <div className="space-y-3">
              {ai.problemStatement && (
                <div>
                  <h3 className="font-semibold">Problem Statement</h3>
                  <p className="text-gray-800">{ai.problemStatement}</p>
                </div>
              )}
              {ai.details && (
                <div>
                  <h3 className="font-semibold">Details</h3>
                  <p className="text-gray-800 whitespace-pre-wrap">
                    {ai.details}
                  </p>
                </div>
              )}
              {ai.taskDetails && (
                <div>
                  <h3 className="font-semibold">Task Breakdown</h3>
                  <pre className="bg-gray-100 p-2 rounded text-sm whitespace-pre-wrap">
                    {ai.taskDetails}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
