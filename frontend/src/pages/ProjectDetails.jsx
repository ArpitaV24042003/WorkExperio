import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";

export default function ProjectDetails() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [project, setProject] = useState(null);
  const [team, setTeam] = useState(null);
  const [teamMembers, setTeamMembers] = useState([]);
  const [memberDetails, setMemberDetails] = useState({}); // {user_id: {name, email}}
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadProject = async () => {
      try {
        const { data } = await apiClient.get(`/projects/${projectId}`).catch((err) => {
          if (err.response?.status === 401 || err.response?.status === 403) {
            setError("You don't have access to this project");
            // Don't navigate immediately - let user see the error
            return null;
          }
          throw err;
        });
        
        if (!data) {
          setLoading(false);
          return;
        }
        
        setProject(data);
        
        // Load team if it exists
        if (data.team_id) {
          try {
            const teamData = await apiClient.get(`/teams/projects/${projectId}/team`).catch(handleApiError);
            setTeam(teamData.data.team);
            const members = teamData.data.members || [];
            setTeamMembers(members);
            
            // Fetch user details for each member
            const details = {};
            for (const member of members) {
              try {
                const userData = await apiClient.get(`/users/${member.user_id}/profile`).catch(() => null);
                if (userData?.data) {
                  details[member.user_id] = {
                    name: userData.data.name || member.user_id,
                    email: userData.data.email || "",
                  };
                } else {
                  details[member.user_id] = { name: member.user_id, email: "" };
                }
              } catch {
                details[member.user_id] = { name: member.user_id, email: "" };
              }
            }
            setMemberDetails(details);
          } catch (err) {
            console.error("Failed to load team:", err);
          }
        }
      } catch (error) {
        console.error(error);
        setError(error.message || "Failed to load project");
      } finally {
        setLoading(false);
      }
    };
    loadProject();
  }, [projectId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <p className="text-sm text-muted-foreground">Loading project...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <p className="text-sm text-destructive">{error || "Project not found or you don't have access to it."}</p>
        <div className="flex gap-2">
          <Button asChild>
            <Link to="/projects">Back to Projects</Link>
          </Button>
          <Button variant="outline" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

  const isTeamLeader = project?.owner_id === user?.id;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-semibold">{project.title}</h1>
          <p className="text-muted-foreground">{project.description}</p>
        </div>
        <div className="flex gap-2">
          <Badge variant="outline">Team: {project.team_type}</Badge>
          {isTeamLeader && <Badge variant="secondary">Team Leader</Badge>}
        </div>
      </div>

      {/* Team Members Display */}
      {team && teamMembers.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Team Members</CardTitle>
            <CardDescription>Your project team ({teamMembers.length} member{teamMembers.length !== 1 ? "s" : ""})</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {teamMembers.map((member) => {
                const isLeader = member.user_id === project.owner_id;
                const memberInfo = memberDetails[member.user_id] || { name: member.user_id, email: "" };
                return (
                  <div key={member.id} className="flex items-center justify-between rounded-md border p-3">
                    <div className="flex items-center gap-3 flex-1">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{memberInfo.name}</p>
                          {isLeader && <Badge variant="secondary">Leader</Badge>}
                        </div>
                        {memberInfo.email && (
                          <p className="text-xs text-muted-foreground">{memberInfo.email}</p>
                        )}
                        {member.role && (
                          <p className="text-sm text-muted-foreground mt-1">Role: {member.role}</p>
                        )}
                        <p className="text-xs text-muted-foreground mt-1">
                          Joined: {new Date(member.joined_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Actions</CardTitle>
          <CardDescription>Collaborate, manage teams, and use AI copilots.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          {!team && (
            <Button asChild>
              <Link to={`/projects/${project.id}/team`}>Team formation</Link>
            </Button>
          )}
          {team && (
            <Button variant="outline" asChild>
              <Link to={`/projects/${project.id}/team`}>Manage Team</Link>
            </Button>
          )}
          {team && (
            <Button variant="outline" asChild>
              <Link to={`/projects/${project.id}/chat`}>Team chat</Link>
            </Button>
          )}
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

