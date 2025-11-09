import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Bell, UserCircle } from "lucide-react";
import bg from "../assets/Profilepicture.jpeg";
import { apiRequest } from "../api";

export default function DashboardPage() {
  const navigate = useNavigate();
  const [me, setMe] = useState(null);
  const [latestProject, setLatestProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState(null);

  useEffect(() => {
    let ignore = false;
    (async () => {
      setLoading(true);
      setApiError(null);
      try {
        const user = await apiRequest("/users/me");
        if (!ignore) setMe(user);

        // get the most recent project owned by the user
        const projects = await apiRequest(
          "/projects?mine=true&limit=1&sort=createdAt:desc"
        );
        if (!ignore)
          setLatestProject(Array.isArray(projects) ? projects[0] : null);
      } catch (e) {
        if (!ignore) setApiError(e?.message || "Failed to load dashboard");
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    return () => (ignore = true);
  }, []);

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
            <Link to="/profile">
              <UserCircle className="w-8 h-8 cursor-pointer" />
            </Link>
          </div>
        </div>

        <div className="bg-white bg-opacity-90 p-8 rounded-2xl shadow-lg">
          {apiError && (
            <div className="mb-4 p-3 rounded bg-yellow-100 text-yellow-800">
              {apiError}
            </div>
          )}

          {/* Greeting */}
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            {loading ? (
              "Loading..."
            ) : (
              <>
                Welcome back,{" "}
                <span className="text-blue-600">{me?.name || "Student"}</span>
              </>
            )}
          </h2>
          <p className="text-gray-700 mb-6">{me?.email || ""}</p>

          {/* Current project summary or empty state */}
          <div className="border rounded-lg shadow p-6 mb-6">
            <div className="bg-cyan-600 text-white font-semibold px-4 py-2 rounded-t-lg -mx-6 -mt-6 mb-4">
              Current Project Summary
            </div>

            {loading ? (
              <p className="text-gray-600">Loading your latest project…</p>
            ) : latestProject ? (
              <>
                <h3 className="text-lg font-bold mb-2">{latestProject.name}</h3>
                <p className="text-gray-700 mb-4">
                  <strong>Domain:</strong> {latestProject.domain} &nbsp;•&nbsp;
                  <strong>Skill:</strong> {latestProject.skillLevel || "—"}{" "}
                  &nbsp;•&nbsp;
                  <strong>Phase:</strong> {latestProject.phase || "—"}
                </p>
                <div className="flex gap-3">
                  <Link to={`/projects/${latestProject.id}`}>
                    <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded shadow-md font-semibold transition">
                      Open Project
                    </button>
                  </Link>
                  <Link to="/projects">
                    <button className="bg-gray-200 hover:bg-gray-300 text-gray-900 px-4 py-2 rounded shadow-md font-semibold transition">
                      View All Projects
                    </button>
                  </Link>
                </div>
              </>
            ) : (
              <div className="text-gray-700">
                <p className="mb-4">You don’t have any projects yet.</p>
                <Link to="/new-project">
                  <button className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg shadow-md font-semibold transition">
                    Create Your First Project
                  </button>
                </Link>
              </div>
            )}
          </div>

          {/* Quick links */}
          <div className="mt-6 text-center">
            <Link to="/projects">
              <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg shadow-md font-semibold transition">
                Go to Projects
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
