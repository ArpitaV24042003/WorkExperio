import { useEffect, useState } from "react";
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
import ErrorBoundary from "./components/ErrorBoundary";

const ProtectedRoute = ({ children }) => {
  const { initialize, token } = useAuthStore();
  const [isChecking, setIsChecking] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // Initialize auth state on mount (for page refresh)
  useEffect(() => {
    // Always initialize from localStorage first
    initialize();
    
    // Check token in localStorage directly (more reliable)
    const storedToken = localStorage.getItem("token");
    const hasValidToken = storedToken && storedToken.trim().length > 0;
    
    // Update store if token exists but not in store
    if (hasValidToken && !token) {
      initialize();
    }
    
    // Set authenticated state immediately
    setIsAuthenticated(hasValidToken || Boolean(token));
    
    // Mark checking as complete
    setIsChecking(false);
  }, [initialize, token]);
  
  // Show loading while checking auth (only briefly)
  if (isChecking) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    );
  }
  
  // Check if authenticated - prioritize localStorage check
  const storedToken = localStorage.getItem("token");
  const hasAuth = (storedToken && storedToken.trim().length > 0) || (token && token.trim().length > 0);
  
  if (!hasAuth) {
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
    <ErrorBoundary>
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
    </ErrorBoundary>
  );
}
