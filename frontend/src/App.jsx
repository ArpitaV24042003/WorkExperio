import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import LoginSignupPage from "./pages/LoginSignupPage";
import ProfilePage from "./pages/ProfilePage";
import DashboardPage from "./pages/DashboardPage";
import ProjectSectionPage from "./pages/ProjectSectionPage";
import NewProjectFlow from "./pages/NewProjectFlow";
import ProjectDashboardPage from "./pages/ProjectDashboardPage";



import "./App.css";

export default function App() {
  return (
    <Router>
      <Routes>
        {/* General routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginSignupPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/projects" element={<ProjectSectionPage />} />
        <Route path="/new-project" element={<NewProjectFlow />} />
        
        {/* Project Dashboard */}
        <Route path="/project-dashboard" element={<ProjectDashboardPage />} />
         
        {/* Sub-pages from sidebar */}
        
       

        
      </Routes>
    </Router>
  );
}
