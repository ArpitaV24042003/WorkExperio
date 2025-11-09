// import { Link } from "react-router-dom";
// import { useState } from "react";
// import bg from "../assets/Profilepicture.jpeg";
// import { Bell, UserCircle } from "lucide-react";
// import { apiRequest } from "../api";

// export default function DashboardPage() {
//   const [role] = useState("Frontend Developer");              // 👉 example role
//   const [compatibility] = useState(85);                       // 👉 example %

//   const showProjectInfo = () => {
//     alert(
//       `AI-Powered Career Guidance\n\n` +
//         `Description: A web-based platform that uses AI/ML to analyze student resumes, extract skills, and recommend career paths.\n\n` +
//         `Your Role: Frontend Developer\n` +
//         `Current Phase: Phase 3 — Development in Progress\n\n` +
//         `Team:\n - Alice (Project Manager)\n - Bob (Backend Developer)\n - Charlie (Frontend Developer - You)\n - Diana (Data Scientist)`
//     );
//   };

//   return (
//     <div className="min-h-screen bg-cover bg-center" style={{ backgroundImage: `url(${bg})` }}>
//       {/* Overlay */}
//       <div className="min-h-screen bg-black bg-opacity-50 p-6">
//         {/* Header */}
//         <div className="flex items-center justify-between text-white mb-6">
//           <h1 className="text-2xl font-bold">WorkExperio</h1>
//           <div className="flex items-center gap-4">
//             <Bell className="w-6 h-6 cursor-pointer" />
//             <Link to="/profile">
//               <UserCircle className="w-8 h-8 cursor-pointer" />
//             </Link>
//           </div>
//         </div>

//         <div className="bg-white bg-opacity-90 p-8 rounded-2xl shadow-lg">
//           {/* Greeting */}
//           <h2 className="text-2xl font-bold text-gray-800 mb-2">
//             Welcome back, <span className="text-blue-600">Student Name</span>
//           </h2>

//           {/* NEW LINE */}
//           <p className="text-gray-700 mb-6">
//   {role} — {compatibility}% Compatibility for this role based on your Skills, Any Changes needed?{" "}
//   <Link to="/profile" className="text-blue-600 underline">
//     Edit
//   </Link>
// </p>

//           {/* Quick Stats */}
//           <div className="bg-cyan-600 text-white font-semibold px-4 py-2 rounded-t-lg">
//             Quick Stats
//           </div>
//           <div className="border border-cyan-600 rounded-b-lg p-6 mb-6 bg-white">
//             <p className="text-gray-600">No stats yet...</p>
//           </div>

//           {/* Project Summary */}
//           <div className="border rounded-lg shadow p-6 mb-6">
//             <div className="bg-cyan-600 text-white font-semibold px-4 py-2 rounded-t-lg -mx-6 -mt-6 mb-4">
//               Current Project Summary
//             </div>
//             <h3 className="text-lg font-bold mb-2">AI-Powered Career Guidance</h3>
//             <button
//               onClick={showProjectInfo}
//               className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded shadow-md font-semibold transition"
//             >
//               Open
//             </button>
//           </div>

//           {/* Project Section Button */}
//           <div className="mt-6 text-center">
//             <Link to="/projects">
//               <button className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg shadow-md font-semibold transition">
//                 Go to Project Section
//               </button>
//             </Link>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }

import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import bg from "../assets/Profilepicture.jpeg";
import { Bell, UserCircle } from "lucide-react";
import { apiRequest } from "../api";

export default function DashboardPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // Ensure a user is present (basic guard)
  useEffect(() => {
    const raw = localStorage.getItem("user");
    if (!raw) {
      navigate("/");
      return;
    }
    try {
      const u = JSON.parse(raw);
      setUser(u);
    } catch {
      localStorage.removeItem("user");
      navigate("/");
    }
  }, [navigate]);

  // Try fetching richer profile data (optional)
  useEffect(() => {
    let ignore = false;
    async function load() {
      try {
        const me = await apiRequest("/users/me", "GET");
        if (!ignore) setProfile(me);
      } catch {
        // If /users/me is not available, fall back to localStorage user
      } finally {
        if (!ignore) setLoading(false);
      }
    }
    load();
    return () => (ignore = true);
  }, []);

  const displayName = profile?.name || user?.name || user?.email || "there";
  const role = profile?.role || user?.role || "Member";
  const compatibility = profile?.compatibility; // number if provided
  const lastLogin = localStorage.getItem("lastLogin");

  const showProjectInfo = () => {
    alert(
      `AI-Powered Career Guidance\n\n` +
        `Description: A web-based platform that uses AI/ML to analyze student resumes, extract skills, and recommend career paths.\n\n` +
        `Your Role: ${role}\n` +
        `Current Phase: Phase 3 — Development in Progress\n\n` +
        `Team:\n - Alice (Project Manager)\n - Bob (Backend Developer)\n - ${displayName} (${role})\n - Diana (Data Scientist)`
    );
  };

  const logout = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div
      className="min-h-screen bg-cover bg-center"
      style={{ backgroundImage: `url(${bg})` }}
    >
      <div className="min-h-screen bg-black bg-opacity-50 p-6">
        {/* Header */}
        <div className="flex items-center justify-between text-white mb-6">
          <h1 className="text-2xl font-bold">WorkExperio</h1>
          <div className="flex items-center gap-4">
            <Bell className="w-6 h-6 cursor-pointer" />
            <button onClick={logout} className="underline">
              Logout
            </button>
            <Link to="/profile">
              <UserCircle className="w-8 h-8 cursor-pointer" />
            </Link>
          </div>
        </div>

        <div className="bg-white bg-opacity-90 p-8 rounded-2xl shadow-lg">
          {/* Greeting */}
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Welcome back, <span className="text-blue-600">{displayName}</span>
          </h2>

          <p className="text-gray-700 mb-6">
            {role}
            {typeof compatibility === "number" ? (
              <> — {compatibility}% compatibility</>
            ) : null}
            {lastLogin ? (
              <> • Last login: {new Date(lastLogin).toLocaleString()}</>
            ) : null}{" "}
            <Link to="/profile" className="text-blue-600 underline">
              Edit
            </Link>
          </p>

          {/* Quick Stats */}
          <div className="bg-cyan-600 text-white font-semibold px-4 py-2 rounded-t-lg">
            Quick Stats
          </div>
          <div className="border border-cyan-600 rounded-b-lg p-6 mb-6 bg-white">
            {loading ? (
              <p className="text-gray-600">Loading…</p>
            ) : profile ? (
              <ul className="list-disc pl-6 text-gray-700">
                {profile.skills?.length ? (
                  <li>Skills: {profile.skills.join(", ")}</li>
                ) : null}
                {typeof profile.projectsCompleted === "number" ? (
                  <li>Projects completed: {profile.projectsCompleted}</li>
                ) : null}
                {profile.targetRole ? (
                  <li>Target role: {profile.targetRole}</li>
                ) : null}
                {!profile?.skills &&
                  typeof profile?.projectsCompleted !== "number" &&
                  !profile?.targetRole && (
                    <p className="text-gray-600">No stats yet…</p>
                  )}
              </ul>
            ) : (
              <p className="text-gray-600">No stats yet…</p>
            )}
          </div>

          {/* Project Summary (can be wired to real data later) */}
          <div className="border rounded-lg shadow p-6 mb-6">
            <div className="bg-cyan-600 text-white font-semibold px-4 py-2 rounded-t-lg -mx-6 -mt-6 mb-4">
              Current Project Summary
            </div>
            <h3 className="text-lg font-bold mb-2">
              AI-Powered Career Guidance
            </h3>
            <button
              onClick={showProjectInfo}
              className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded shadow-md font-semibold transition"
            >
              Open
            </button>
          </div>

          <div className="mt-6 text-center">
            <Link to="/projects">
              <button className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg shadow-md font-semibold transition">
                Go to Project Section
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
