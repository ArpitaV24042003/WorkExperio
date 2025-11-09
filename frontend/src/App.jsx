// import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// import LandingPage from "./pages/LandingPage";
// import LoginSignupPage from "./pages/LoginSignupPage";
// import ProfilePage from "./pages/ProfilePage";
// import DashboardPage from "./pages/DashboardPage";
// import ProjectSectionPage from "./pages/ProjectSectionPage";
// import NewProjectFlow from "./pages/NewProjectFlow";
// import ProjectDashboardPage from "./pages/ProjectDashboardPage";

// import "./App.css";

// export default function App() {
//   return (
//     <Router>
//       <Routes>
//         {/* General routes */}
//         <Route path="/" element={<LandingPage />} />
//         <Route path="/login" element={<LoginSignupPage />} />
//         <Route path="/profile" element={<ProfilePage />} />
//         <Route path="/dashboard" element={<DashboardPage />} />
//         <Route path="/projects" element={<ProjectSectionPage />} />
//         <Route path="/new-project" element={<NewProjectFlow />} />

//         {/* Project Dashboard */}
//         <Route path="/project-dashboard" element={<ProjectDashboardPage />} />

//         {/* Sub-pages from sidebar */}

//       </Routes>
//     </Router>
//   );
// }

import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import LoginSignupPage from "./pages/LoginSignupPage";
import ProfilePage from "./pages/ProfilePage";
import DashboardPage from "./pages/DashboardPage";
import ProjectSectionPage from "./pages/ProjectSectionPage"; // your list page
import NewProjectFlow from "./pages/NewProjectFlow";
import ProjectDashboardPage from "./pages/ProjectDashboardPage";
import ProjectHomePage from "./pages/ProjectHomePage"; // NEW

import "./App.css";

function RequireAuth({ children }) {
  const raw = localStorage.getItem("user");
  if (!raw) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Public */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginSignupPage />} />

        {/* Protected */}
        <Route
          path="/profile"
          element={
            <RequireAuth>
              <ProfilePage />
            </RequireAuth>
          }
        />
        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <DashboardPage />
            </RequireAuth>
          }
        />
        <Route
          path="/projects"
          element={
            <RequireAuth>
              <ProjectSectionPage />
            </RequireAuth>
          }
        />
        <Route
          path="/projects/:id"
          element={
            <RequireAuth>
              <ProjectHomePage />
            </RequireAuth>
          }
        />
        <Route
          path="/new-project"
          element={
            <RequireAuth>
              <NewProjectFlow />
            </RequireAuth>
          }
        />
        <Route
          path="/project-dashboard"
          element={
            <RequireAuth>
              <ProjectDashboardPage />
            </RequireAuth>
          }
        />
      </Routes>
    </Router>
  );
}
