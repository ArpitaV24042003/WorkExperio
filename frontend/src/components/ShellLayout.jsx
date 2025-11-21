import { Outlet, NavLink, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { Button } from "./ui/button";
import { Avatar } from "./ui/avatar";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/projects", label: "Projects" },
  { to: "/projects/create", label: "Create Project" },
  { to: "/profile", label: "Profile" },
  { to: "/settings", label: "Settings" },
];

export function ShellLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const handleSignOut = () => {
    logout();
    navigate("/login");
  };

  const onProjectsRoute = location.pathname.startsWith("/projects");

  return (
    <div className="flex min-h-screen bg-muted/20">
      <aside className="hidden w-64 flex-col border-r bg-background p-6 md:flex">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground font-semibold">
            WE
          </div>
          <div>
            <p className="text-lg font-semibold">WorkExperio</p>
            <p className="text-xs text-muted-foreground">Student Collaboration</p>
          </div>
        </div>
        <nav className="flex flex-1 flex-col gap-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  isActive ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto flex items-center justify-between rounded-md border bg-card px-3 py-2">
          <div className="flex items-center gap-2">
            <Avatar name={user?.name} />
            <div>
              <p className="text-sm font-medium">{user?.name ?? "Member"}</p>
              <p className="text-xs text-muted-foreground">{user?.email}</p>
            </div>
          </div>
        </div>
      </aside>
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b bg-background px-4 py-3 shadow-sm">
          <div className="flex items-center gap-3">
            {onProjectsRoute && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate("/projects")}
              >
                ← Back to Projects
              </Button>
            )}
            <p className="text-lg font-semibold">
              {onProjectsRoute ? "Project Workspace" : "WorkExperio"}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2">
              <Avatar name={user?.name} />
              <div className="text-right">
                <p className="text-sm font-medium">{user?.name ?? "Member"}</p>
                <p className="text-xs text-muted-foreground max-w-[180px] truncate">
                  {user?.email}
                </p>
              </div>
            </div>
            <Button
              size="sm"
              onClick={handleSignOut}
              className="bg-black text-black hover:bg-black/90 border border-black"
            >
              Logout
            </Button>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

