import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";

export default function ProjectDetails() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProject = async () => {
      try {
        const { data } = await apiClient.get(`/projects/${projectId}`).catch(handleApiError);
        setProject(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    loadProject();
  }, [projectId]);

  if (loading) {
    return <p className="text-sm text-muted-foreground">Loading project...</p>;
  }

  if (!project) {
    return <p className="text-sm text-destructive">Project not found.</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-semibold">{project.title}</h1>
          <p className="text-muted-foreground">{project.description}</p>
        </div>
        <Badge variant="outline">Team: {project.team_type}</Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Actions</CardTitle>
          <CardDescription>Collaborate, manage teams, and use AI copilots.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button asChild>
            <Link to={`/projects/${project.id}/team`}>Team formation</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to={`/projects/${project.id}/chat`}>Team chat</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to={`/projects/${project.id}/assistant`}>AI assistant</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to={`/projects/${project.id}/performance`}>Performance report</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

