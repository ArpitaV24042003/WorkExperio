// src/App.jsx
import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  Outlet,
  Link,
  useNavigate,
} from "react-router-dom";

import LandingPage from "./pages/LandingPage";
import LoginSignupPage from "./pages/LoginSignupPage";
import ProfilePage from "./pages/ProfilePage";
import DashboardPage from "./pages/DashboardPage";
import ProjectSectionPage from "./pages/ProjectSectionPage";
import NewProjectFlow from "./pages/NewProjectFlow";
import ProjectDashboardPage from "./pages/ProjectDashboardPage";
import ProjectHomePage from "./pages/ProjectHomePage";

import "./App.css";
import { setToken } from "./api";

/* ======= Small Topbar + Profile Badge ======= */
function Topbar() {
  const navigate = useNavigate();

  // Read lightweight user snapshot
  let stored = null;
  try {
    stored = JSON.parse(localStorage.getItem("user") || "null");
  } catch {
    stored = null;
  }

  const name = stored?.name || "";
  const firstName = name ? name.split(" ")[0] : null;

  const handleLogout = () => {
    // Clear local storage and token
    try {
      localStorage.removeItem("user");
      localStorage.removeItem("lastLogin");
      setToken(null);
    } catch (e) {}
    navigate("/login");
  };

  return (
    <nav
      className="topbar"
      style={{ display: "flex", alignItems: "center", padding: "10px 18px" }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <Link
          to="/"
          className="logoHeading"
          style={{ textDecoration: "none", color: "inherit" }}
        >
          <span className="circleLogo" style={{ marginRight: 8 }}>
            w
          </span>
          <i>WorkExperio</i>
        </Link>
        <Link to="/" className="nav-link">
          Home
        </Link>
        {stored ? (
          <Link to="/dashboard" className="nav-link">
            Dashboard
          </Link>
        ) : null}
        <Link to="/projects" className="nav-link">
          Projects
        </Link>
      </div>

      <div
        style={{
          marginLeft: "auto",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        {stored ? (
          <>
            <Link
              to="/profile"
              className="nav-link"
              style={{ padding: "6px 8px", borderRadius: 8 }}
            >
              {firstName ? `Hi, ${firstName}` : "Profile"}
            </Link>
            <button
              onClick={handleLogout}
              className="nav-link"
              style={{
                background: "#e53e3e",
                color: "white",
                border: "none",
                padding: "6px 10px",
                borderRadius: 8,
                cursor: "pointer",
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <Link to="/login" className="nav-link">
            Log In
          </Link>
        )}
      </div>
    </nav>
  );
}

/* ======= Auth guard ======= */
function hasAuth() {
  try {
    const raw = localStorage.getItem("user");
    const token = localStorage.getItem("token");
    if (raw) {
      const u = JSON.parse(raw);
      // Consider user present if id or email exists OR token exists
      return Boolean(u?.id || u?.email || token);
    }
    return Boolean(token);
  } catch {
    return false;
  }
}

function RequireAuth({ children }) {
  if (!hasAuth()) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

/* ======= Layout for protected pages (shows topbar) ======= */
function ProtectedLayout() {
  return (
    <>
      <Topbar />
      <main style={{ padding: 20 }}>
        <Outlet />
      </main>
    </>
  );
}

/* ======= App ======= */
export default function App() {
  const loggedIn = hasAuth();

  return (
    <Router>
      <Routes>
        {/* Root: if logged in -> dashboard, else landing */}
        <Route
          path="/"
          element={
            loggedIn ? <Navigate to="/dashboard" replace /> : <LandingPage />
          }
        />

        {/* Auth pages */}
        <Route path="/login" element={<LoginSignupPage />} />

        {/* Protected routes under layout */}
        <Route
          element={
            <RequireAuth>
              <ProtectedLayout />
            </RequireAuth>
          }
        >
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/projects" element={<ProjectSectionPage />} />
          <Route path="/projects/:id" element={<ProjectHomePage />} />
          <Route path="/new-project" element={<NewProjectFlow />} />
          <Route path="/project-dashboard" element={<ProjectDashboardPage />} />
        </Route>

        {/* Fallback: redirect unknown routes */}
        <Route
          path="*"
          element={<Navigate to={loggedIn ? "/dashboard" : "/"} replace />}
        />
      </Routes>
    </Router>
  );
}
