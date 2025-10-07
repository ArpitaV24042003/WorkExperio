import { Link } from "react-router-dom";
import { useState } from "react";
import bg from "../assets/Profilepicture.jpeg";
import { Bell, UserCircle } from "lucide-react";
import { apiRequest } from "../api";


export default function DashboardPage() {
  const [role] = useState("Frontend Developer");              // 👉 example role
  const [compatibility] = useState(85);                       // 👉 example %
  
  const showProjectInfo = () => {
    alert(
      `AI-Powered Career Guidance\n\n` +
        `Description: A web-based platform that uses AI/ML to analyze student resumes, extract skills, and recommend career paths.\n\n` +
        `Your Role: Frontend Developer\n` +
        `Current Phase: Phase 3 — Development in Progress\n\n` +
        `Team:\n - Alice (Project Manager)\n - Bob (Backend Developer)\n - Charlie (Frontend Developer - You)\n - Diana (Data Scientist)`
    );
  };

  return (
    <div className="min-h-screen bg-cover bg-center" style={{ backgroundImage: `url(${bg})` }}>
      {/* Overlay */}
      <div className="min-h-screen bg-black bg-opacity-50 p-6">
        {/* Header */}
        <div className="flex items-center justify-between text-white mb-6">
          <h1 className="text-2xl font-bold">WorkExperio</h1>
          <div className="flex items-center gap-4">
            <Bell className="w-6 h-6 cursor-pointer" />
            <Link to="/profile">
              <UserCircle className="w-8 h-8 cursor-pointer" />
            </Link>
          </div>
        </div>

        <div className="bg-white bg-opacity-90 p-8 rounded-2xl shadow-lg">
          {/* Greeting */}
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Welcome back, <span className="text-blue-600">Student Name</span>
          </h2>
          
          {/* NEW LINE */}
          <p className="text-gray-700 mb-6">
  {role} — {compatibility}% Compatibility for this role based on your Skills, Any Changes needed?{" "}
  <Link to="/profile" className="text-blue-600 underline">
    Edit
  </Link>
</p>


          {/* Quick Stats */}
          <div className="bg-cyan-600 text-white font-semibold px-4 py-2 rounded-t-lg">
            Quick Stats
          </div>
          <div className="border border-cyan-600 rounded-b-lg p-6 mb-6 bg-white">
            <p className="text-gray-600">No stats yet...</p>
          </div>

          {/* Project Summary */}
          <div className="border rounded-lg shadow p-6 mb-6">
            <div className="bg-cyan-600 text-white font-semibold px-4 py-2 rounded-t-lg -mx-6 -mt-6 mb-4">
              Current Project Summary
            </div>
            <h3 className="text-lg font-bold mb-2">AI-Powered Career Guidance</h3>
            <button
              onClick={showProjectInfo}
              className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded shadow-md font-semibold transition"
            >
              Open
            </button>
          </div>

          {/* Project Section Button */}
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
