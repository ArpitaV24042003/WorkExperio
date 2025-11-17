import { useEffect } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuthStore } from "./store/auth";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import ProfileSetup from "./pages/ProfileSetup";
import Profile from "./pages/Profile";
import UploadResume from "./pages/UploadResume";
import Projects from "./pages/Projects";
import CreateProject from "./pages/CreateProject";
import TeamSuggestions from "./pages/TeamSuggestions";
import ProjectDetails from "./pages/ProjectDetails";
import TeamChat from "./pages/TeamChat";
import AiAssistant from "./pages/AiAssistant";
import PerformanceReport from "./pages/PerformanceReport";
import Settings from "./pages/Settings";
import { ShellLayout } from "./components/ShellLayout";

const ProtectedRoute = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const initialize = useAuthStore((state) => state.initialize);
  
  // Initialize auth state on mount (for page refresh)
  useEffect(() => {
    initialize();
  }, [initialize]);
  
  // Check if token exists in localStorage (for page refresh)
  const hasToken = localStorage.getItem("token");
  if (!isAuthenticated && !hasToken) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

export default function App() {
  const initialize = useAuthStore((state) => state.initialize);
  
  // Initialize auth state on app mount
  useEffect(() => {
    initialize();
  }, [initialize]);
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      <Route
        element={
          <ProtectedRoute>
            <ShellLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile-setup" element={<ProfileSetup />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/upload-resume" element={<UploadResume />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/projects/create" element={<CreateProject />} />
        <Route path="/projects/:projectId" element={<ProjectDetails />} />
        <Route path="/projects/:projectId/team" element={<TeamSuggestions />} />
        <Route path="/projects/:projectId/chat" element={<TeamChat />} />
        <Route path="/projects/:projectId/assistant" element={<AiAssistant />} />
        <Route path="/projects/:projectId/performance" element={<PerformanceReport />} />
        <Route path="/settings" element={<Settings />} />
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
