import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";

export default function Dashboard() {
  const { user, setCredentials, token } = useAuthStore();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Ensure auth is initialized
        const authStore = useAuthStore.getState();
        if (!authStore.isAuthenticated && !authStore.token) {
          authStore.initialize();
        }
        
        const me = await apiClient.get("/users/me").catch(handleApiError);
        if (me?.data) {
          setCredentials({ token: token || authStore.token, user: me.data });
        }
        const { data } = await apiClient.get("/projects").catch(handleApiError);
        setProjects(data || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [setCredentials, token]);

  const xpLevel = user?.level ?? "bronze";

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <div>
          <h1 className="text-3xl font-semibold">Welcome back{user?.name ? `, ${user.name}` : ""}</h1>
          <p className="text-muted-foreground">Build teams, manage projects, and grow your experience points.</p>
        </div>
        <Badge variant="success" className="text-sm">
          Level: {xpLevel?.toUpperCase()}
        </Badge>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Projects</CardTitle>
            <CardDescription>Keep track of upcoming and active collaborations.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold">{projects.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>XP Points</CardTitle>
            <CardDescription>Grow your level by completing project milestones.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold">{user?.xp_points ?? 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Profile Status</CardTitle>
            <CardDescription>Complete your profile to unlock AI recommendations.</CardDescription>
          </CardHeader>
          <CardContent>
            <Badge variant={user?.profile_completed ? "success" : "warning"}>
              {user?.profile_completed ? "Completed" : "Action Required"}
            </Badge>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Your Projects</CardTitle>
            <CardDescription>Recent collaborations and drafts.</CardDescription>
          </div>
          <Button asChild>
            <Link to="/projects/create">Create Project</Link>
          </Button>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading projects...</p>
          ) : projects.length === 0 ? (
            <p className="text-sm text-muted-foreground">No projects yet. Create your first collaboration.</p>
          ) : (
            <div className="space-y-4">
              {projects.map((project) => (
                <div key={project.id} className="flex items-center justify-between rounded-md border p-4">
                  <div>
                    <p className="font-medium">{project.title}</p>
                    <p className="text-sm text-muted-foreground">{project.description}</p>
                  </div>
                  <Button variant="outline" asChild>
                    <Link to={`/projects/${project.id}`}>View</Link>
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

