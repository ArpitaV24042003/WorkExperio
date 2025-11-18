import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        setError("");
        const { data } = await apiClient.get("/projects", { timeout: 10000 }).catch(handleApiError);
        setProjects(data || []);
      } catch (error) {
        console.error("Failed to fetch projects:", error);
        const errorMessage = error?.response?.data?.detail || error.message || "Failed to load projects. Please try again.";
        setError(errorMessage);
        setProjects([]); // Ensure projects is empty array on error
      } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold">Projects</h1>
          <p className="text-muted-foreground">Manage collaborations, track waitlists, and monitor team activity.</p>
        </div>
        <Button asChild>
          <Link to="/projects/create">New Project</Link>
        </Button>
      </div>

      {error && (
        <Card>
          <CardContent className="p-6">
            <p className="text-sm text-destructive">{error}</p>
            <Button 
              onClick={() => window.location.reload()} 
              variant="outline" 
              className="mt-2"
            >
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <p className="text-sm text-muted-foreground">Loading projects...</p>
      ) : !error && projects.length === 0 ? (
        <Card>
          <CardContent className="p-6 text-sm text-muted-foreground">
            No projects yet. Create one to get started with AI team formation.
          </CardContent>
        </Card>
      ) : !error && (
        <div className="grid gap-4 md:grid-cols-2">
          {projects.map((project) => (
            <Card key={project.id}>
              <CardHeader>
                <CardTitle className="flex justify-between">
                  {project.title}
                  <Badge variant={project.ai_generated ? "default" : "secondary"}>
                    {project.ai_generated ? "AI-generated" : "Manual"}
                  </Badge>
                </CardTitle>
                <CardDescription>{project.description}</CardDescription>
              </CardHeader>
              <CardContent className="flex items-center justify-between">
                <Badge variant="outline">Team: {project.team_type}</Badge>
                <div className="flex gap-2">
                  <Button variant="outline" asChild>
                    <Link to={`/projects/${project.id}`}>View</Link>
                  </Button>
                  <Button variant="outline" asChild>
                    <Link to={`/projects/${project.id}/team`}>Team</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

