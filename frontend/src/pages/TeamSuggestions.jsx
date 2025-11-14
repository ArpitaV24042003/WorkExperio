import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Badge } from "../components/ui/badge";

export default function TeamSuggestions() {
  const { projectId } = useParams();
  const { user } = useAuthStore();
  const [candidateId, setCandidateId] = useState("");
  const [candidateSkills, setCandidateSkills] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [suggestion, setSuggestion] = useState(null);
  const [teamRoles, setTeamRoles] = useState({});
  const [waitlistStatus, setWaitlistStatus] = useState(null);
  const [message, setMessage] = useState("");

  const addCandidate = () => {
    if (!candidateId) return;
    setCandidates((prev) => [
      ...prev,
      {
        user_id: candidateId,
        skills: candidateSkills.split(",").map((skill) => skill.trim()).filter(Boolean),
      },
    ]);
    setCandidateId("");
    setCandidateSkills("");
  };

  const fetchSuggestion = async () => {
    setMessage("");
    try {
      const payload = {
        project_id: projectId,
        required_skills: candidates.flatMap((candidate) => candidate.skills),
        candidate_profiles: candidates,
      };
      const { data } = await apiClient.post("/ml/team-selection", payload).catch(handleApiError);
      setSuggestion(data);
    } catch (error) {
      setMessage(error.message);
    }
  };

  const assignTeam = async () => {
    if (!suggestion?.recommended_team?.length) {
      setMessage("Generate a team suggestion first.");
      return;
    }
    try {
      await apiClient.post(`/projects/${projectId}/assign-team`, {
        project_id: projectId,
        user_ids: suggestion.recommended_team,
        role_map: teamRoles,
      });
      setMessage("Team assigned successfully.");
    } catch (error) {
      setMessage(error.message);
    }
  };

  const joinWaitlist = async () => {
    try {
      await apiClient.post(`/projects/${projectId}/waitlist`, { user_id: user?.id });
      setMessage("Joined waitlist. We'll notify you about solo fallback.");
      await fetchWaitlistStatus();
    } catch (error) {
      setMessage(error.message);
    }
  };

  const fetchWaitlistStatus = async () => {
    try {
      const { data } = await apiClient.get(`/projects/${projectId}/waitlist-status`).catch(handleApiError);
      setWaitlistStatus(data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchWaitlistStatus();
  }, [projectId]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold">Team suggestions</h1>
        <p className="text-muted-foreground">Collect candidate profiles and let AI recommend a balanced team.</p>
      </div>

      {message ? <p className="text-sm text-muted-foreground">{message}</p> : null}

      <Card>
        <CardHeader>
          <CardTitle>Candidate pool</CardTitle>
          <CardDescription>Add potential teammates with their skill tags.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="candidateId">Candidate ID</Label>
              <Input id="candidateId" value={candidateId} onChange={(event) => setCandidateId(event.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="candidateSkills">Skills (comma separated)</Label>
              <Input
                id="candidateSkills"
                value={candidateSkills}
                onChange={(event) => setCandidateSkills(event.target.value)}
              />
            </div>
          </div>
          <Button type="button" onClick={addCandidate} variant="outline">
            Add candidate
          </Button>

          <div className="space-y-2">
            {candidates.length ? (
              candidates.map((candidate) => (
                <div key={candidate.user_id} className="flex items-center justify-between rounded-md border p-3">
                  <p className="font-medium">{candidate.user_id}</p>
                  <div className="flex flex-wrap gap-1">
                    {candidate.skills.map((skill) => (
                      <Badge key={skill} variant="outline">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">Add candidates to generate suggestions.</p>
            )}
          </div>

          <Button type="button" onClick={fetchSuggestion}>
            Generate team
          </Button>
        </CardContent>
      </Card>

      {suggestion ? (
        <Card>
          <CardHeader>
            <CardTitle>Recommended team</CardTitle>
            <CardDescription>Assign roles and confirm your selection.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {suggestion.recommended_team.map((memberId) => (
              <div key={memberId} className="grid gap-2 md:grid-cols-[1fr_200px]">
                <div>
                  <p className="font-medium">{memberId}</p>
                  <p className="text-xs text-muted-foreground">
                    Match score:{" "}
                    {
                      suggestion.scoring.find((score) => score.user_id === memberId)?.match_score
                    }
                  </p>
                </div>
                <Input
                  placeholder="Role (e.g., Lead Developer)"
                  value={teamRoles[memberId] ?? ""}
                  onChange={(event) =>
                    setTeamRoles((prev) => ({
                      ...prev,
                      [memberId]: event.target.value,
                    }))
                  }
                />
              </div>
            ))}
            <Button type="button" onClick={assignTeam}>
              Assign team
            </Button>
          </CardContent>
        </Card>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Waitlist & Solo fallback</CardTitle>
          <CardDescription>Track time remaining before automatic solo assignment.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button variant="outline" onClick={joinWaitlist}>
            Join waitlist
          </Button>
          {waitlistStatus ? (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Auto solo assignment date:{" "}
                {waitlistStatus.auto_solo_at ? new Date(waitlistStatus.auto_solo_at).toLocaleString() : "Pending"}
              </p>
              <div className="space-y-2">
                {waitlistStatus.entries.map((entry) => (
                  <div key={entry.id} className="flex items-center justify-between rounded-md border p-2">
                    <span className="text-sm">{entry.user_id}</span>
                    <Badge variant="outline">{entry.days_left} days left</Badge>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No waitlist entries yet.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

