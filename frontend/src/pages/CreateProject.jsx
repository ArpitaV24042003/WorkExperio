import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Badge } from "../components/ui/badge";

export default function CreateProject() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [step, setStep] = useState(1); // 1: Team Formation, 2: AI Generation, 3: Create Project
  const [profile, setProfile] = useState(null);
  const [teamMembers, setTeamMembers] = useState([]);
  const [teamFormationMode, setTeamFormationMode] = useState("manual"); // manual, skill_match, interest_match, waitlist
  const [manualMemberId, setManualMemberId] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [searchMode, setSearchMode] = useState("email"); // email, name, user_id
  const [form, setForm] = useState({ title: "", description: "", ai_generated: false, team_type: "none" });
  const [aiIdea, setAiIdea] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchProfile = async () => {
      if (!user?.id) return;
      try {
        const { data } = await apiClient.get(`/users/${user.id}/profile`).catch(handleApiError);
        setProfile(data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchProfile();
  }, [user?.id]);

  const handleChange = (event) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const searchUsers = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    
    setSearching(true);
    try {
      let endpoint = "";
      if (searchMode === "email") {
        endpoint = `/users/search/by-email?email=${encodeURIComponent(searchQuery)}`;
        const { data } = await apiClient.get(endpoint).catch(handleApiError);
        setSearchResults(data ? [data] : []);
      } else if (searchMode === "name") {
        endpoint = `/users/search/by-name?name=${encodeURIComponent(searchQuery)}&limit=5`;
        const { data } = await apiClient.get(endpoint).catch(handleApiError);
        setSearchResults(data || []);
      } else {
        // user_id mode - if it looks like a valid UUID, just add it directly
        // User can add it via the direct User ID input below
        setSearchResults([]);
      }
    } catch (err) {
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const addMemberFromSearch = (user) => {
    const userId = user.user_id || user.id;
    if (userId && !teamMembers.includes(userId)) {
      setTeamMembers([...teamMembers, userId]);
      setSearchQuery("");
      setSearchResults([]);
    }
  };

  const addManualMember = () => {
    if (manualMemberId && !teamMembers.includes(manualMemberId)) {
      setTeamMembers([...teamMembers, manualMemberId]);
      setManualMemberId("");
    }
  };

  const removeMember = (memberId) => {
    setTeamMembers(teamMembers.filter((id) => id !== memberId));
  };

  const handleTeamFormationNext = async () => {
    setLoading(true);
    setError("");
    
    try {
      // If skill_match or interest_match, find team members automatically
      if (teamFormationMode === "skill_match" || teamFormationMode === "interest_match") {
        const userSkills = profile?.skills?.map((skill) => skill.name) || [];
        const skillsQuery = userSkills.join(",");
        
        const endpoint = teamFormationMode === "skill_match" 
          ? `/users/search/by-skills?skills=${encodeURIComponent(skillsQuery)}&limit=5`
          : `/users/search/by-interests?interests=${encodeURIComponent(skillsQuery)}&limit=5`;
        
        const { data } = await apiClient.get(endpoint).catch(handleApiError);
        
        if (data && data.length > 0) {
          // Add top matching users to team
          const matchedMembers = data.slice(0, 3).map((user) => user.user_id);
          setTeamMembers([...teamMembers, ...matchedMembers]);
        }
      }
      
      if (teamFormationMode === "waitlist") {
        setForm((prev) => ({ ...prev, team_type: "waitlist" }));
      } else if (teamMembers.length > 0) {
        setForm((prev) => ({ ...prev, team_type: "team" }));
      } else {
        setForm((prev) => ({ ...prev, team_type: "none" }));
      }
      setStep(2); // Move to AI generation step
    } catch (err) {
      setError(err.message || "Failed to find team members");
    } finally {
      setLoading(false);
    }
  };

  const generateAiIdeaFromTeam = async () => {
    setLoading(true);
    setError("");
    try {
      // Collect current user's skills
      const currentUserSkills = profile?.skills?.map((skill) => skill.name) ?? [];
      
      // Pass team member IDs - backend will fetch their skills
      const payload = {
        skills: currentUserSkills, // Base skills from current user
        experience_level: profile?.experiences?.length ? "intermediate" : "beginner",
        candidate_profiles: teamMembers.map((id) => ({ user_id: id, skills: [] })), // Backend will fetch skills
      };
      
      const { data } = await apiClient.post("/projects/ai-generate", payload).catch(handleApiError);
      setAiIdea(data);
      setForm((prev) => ({
        ...prev,
        title: data.title || prev.title,
        description: data.description || prev.description,
        ai_generated: true,
      }));
      setStep(3); // Move to project creation step
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createProject = async (event) => {
    event.preventDefault();
    if (!form.title || !form.description) {
      setError("Title and description are required. Use AI generation if needed.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const { data } = await apiClient.post("/projects", form).catch(handleApiError);
      // If team was formed, assign it to the project
      if (teamMembers.length > 0 && data.id) {
        try {
          await apiClient.post(`/teams/projects/${data.id}/assign-team`, {
            project_id: data.id,
            user_ids: teamMembers,
            role_map: {},
          });
        } catch (teamErr) {
          console.error("Failed to assign team:", teamErr);
        }
      }
      navigate(`/projects/${data.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Step Indicator */}
      <div className="flex items-center justify-center gap-4">
        <div className={`flex items-center gap-2 ${step >= 1 ? "text-primary" : "text-muted-foreground"}`}>
          <div className={`flex h-8 w-8 items-center justify-center rounded-full border-2 ${step >= 1 ? "border-primary bg-primary text-primary-foreground" : "border-muted"}`}>
            1
          </div>
          <span className="font-medium">Team Formation</span>
        </div>
        <div className={`h-1 w-16 ${step >= 2 ? "bg-primary" : "bg-muted"}`} />
        <div className={`flex items-center gap-2 ${step >= 2 ? "text-primary" : "text-muted-foreground"}`}>
          <div className={`flex h-8 w-8 items-center justify-center rounded-full border-2 ${step >= 2 ? "border-primary bg-primary text-primary-foreground" : "border-muted"}`}>
            2
          </div>
          <span className="font-medium">AI Generation</span>
        </div>
        <div className={`h-1 w-16 ${step >= 3 ? "bg-primary" : "bg-muted"}`} />
        <div className={`flex items-center gap-2 ${step >= 3 ? "text-primary" : "text-muted-foreground"}`}>
          <div className={`flex h-8 w-8 items-center justify-center rounded-full border-2 ${step >= 3 ? "border-primary bg-primary text-primary-foreground" : "border-muted"}`}>
            3
          </div>
          <span className="font-medium">Create Project</span>
        </div>
      </div>

      {error ? <p className="text-sm text-destructive text-center">{error}</p> : null}

      {/* Step 1: Team Formation */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Form Your Team</CardTitle>
            <CardDescription>Choose how you want to form your team. You can add members manually, match by skills/interests, or use waitlist.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Team Formation Mode Selection */}
            <div className="space-y-3">
              <Label>Team Formation Method</Label>
              <div className="grid gap-3 md:grid-cols-2">
                <button
                  type="button"
                  onClick={() => setTeamFormationMode("manual")}
                  className={`rounded-md border p-4 text-left transition-colors ${
                    teamFormationMode === "manual" ? "border-primary bg-primary/5" : "border-muted"
                  }`}
                >
                  <p className="font-medium">Add Known Members</p>
                  <p className="text-xs text-muted-foreground">Add team members if you know their user IDs</p>
                </button>
                <button
                  type="button"
                  onClick={() => setTeamFormationMode("skill_match")}
                  className={`rounded-md border p-4 text-left transition-colors ${
                    teamFormationMode === "skill_match" ? "border-primary bg-primary/5" : "border-muted"
                  }`}
                >
                  <p className="font-medium">Match by Skills</p>
                  <p className="text-xs text-muted-foreground">AI will find members with similar skills</p>
                </button>
                <button
                  type="button"
                  onClick={() => setTeamFormationMode("interest_match")}
                  className={`rounded-md border p-4 text-left transition-colors ${
                    teamFormationMode === "interest_match" ? "border-primary bg-primary/5" : "border-muted"
                  }`}
                >
                  <p className="font-medium">Match by Interests</p>
                  <p className="text-xs text-muted-foreground">AI will find members with similar interests</p>
                </button>
                <button
                  type="button"
                  onClick={() => setTeamFormationMode("waitlist")}
                  className={`rounded-md border p-4 text-left transition-colors ${
                    teamFormationMode === "waitlist" ? "border-primary bg-primary/5" : "border-muted"
                  }`}
                >
                  <p className="font-medium">Waitlist</p>
                  <p className="text-xs text-muted-foreground">Join waitlist for team assignment</p>
                </button>
              </div>
            </div>

            {/* Manual Member Addition */}
            {teamFormationMode === "manual" && (
              <div className="space-y-3">
                <Label>Add Team Members</Label>
                <p className="text-xs text-muted-foreground">
                  Search by email or name, or enter user ID directly. Your User ID is shown in your Profile page.
                </p>
                
                {/* Search Mode Toggle */}
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant={searchMode === "email" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSearchMode("email")}
                  >
                    Email
                  </Button>
                  <Button
                    type="button"
                    variant={searchMode === "name" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSearchMode("name")}
                  >
                    Name
                  </Button>
                  <Button
                    type="button"
                    variant={searchMode === "user_id" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSearchMode("user_id")}
                  >
                    User ID
                  </Button>
                </div>

                {/* Search Input */}
                <div className="flex gap-2">
                  <Input
                    placeholder={
                      searchMode === "email" 
                        ? "Enter email address" 
                        : searchMode === "name"
                        ? "Enter name to search"
                        : "Enter user ID"
                    }
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      if (searchMode === "name" && e.target.value.length >= 2) {
                        searchUsers();
                      }
                    }}
                    onKeyPress={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        if (searchMode === "user_id") {
                          setManualMemberId(searchQuery);
                          addManualMember();
                          setSearchQuery("");
                        } else {
                          searchUsers();
                        }
                      }
                    }}
                  />
                  {searchMode !== "name" && (
                    <Button type="button" onClick={searchUsers} variant="outline" disabled={searching}>
                      {searching ? "Searching..." : "Search"}
                    </Button>
                  )}
                </div>

                {/* Search Results */}
                {searchResults.length > 0 && (
                  <div className="space-y-2 rounded-md border p-3">
                    <p className="text-sm font-medium">Search Results:</p>
                    {searchResults.map((user) => {
                      const userId = user.user_id || user.id;
                      const isAdded = teamMembers.includes(userId);
                      return (
                        <div
                          key={userId}
                          className={`flex items-center justify-between rounded-md border p-2 ${
                            isAdded ? "bg-muted opacity-50" : "cursor-pointer hover:bg-muted/50"
                          }`}
                          onClick={() => !isAdded && addMemberFromSearch(user)}
                        >
                          <div>
                            <p className="font-medium">{user.name}</p>
                            <p className="text-xs text-muted-foreground">{user.email}</p>
                            {user.skills && user.skills.length > 0 && (
                              <div className="mt-1 flex flex-wrap gap-1">
                                {user.skills.slice(0, 3).map((skill, idx) => (
                                  <Badge key={idx} variant="outline" className="text-xs">
                                    {skill}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </div>
                          {isAdded ? (
                            <Badge variant="secondary">Added</Badge>
                          ) : (
                            <Button type="button" size="sm" variant="outline">
                              Add
                            </Button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Direct User ID Input (fallback) */}
                <div className="space-y-2">
                  <Label htmlFor="directUserId" className="text-xs text-muted-foreground">
                    Or enter User ID directly:
                  </Label>
                  <div className="flex gap-2">
                    <Input
                      id="directUserId"
                      placeholder="User ID (from Profile page)"
                      value={manualMemberId}
                      onChange={(e) => setManualMemberId(e.target.value)}
                      onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addManualMember())}
                    />
                    <Button type="button" onClick={addManualMember} variant="outline">
                      Add
                    </Button>
                  </div>
                </div>

                {/* Team Members List */}
                {teamMembers.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Team Members ({teamMembers.length}):</p>
                    <div className="flex flex-wrap gap-2">
                      {teamMembers.map((memberId) => (
                        <Badge key={memberId} variant="secondary" className="flex items-center gap-2">
                          {memberId}
                          <button
                            type="button"
                            onClick={() => removeMember(memberId)}
                            className="ml-1 hover:text-destructive"
                          >
                            ×
                          </button>
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Skill/Interest Match Info */}
            {(teamFormationMode === "skill_match" || teamFormationMode === "interest_match") && (
              <div className="rounded-md border border-muted bg-muted/50 p-4">
                <p className="text-sm text-muted-foreground">
                  AI will automatically match team members based on {teamFormationMode === "skill_match" ? "skills" : "interests"} after you generate the project idea.
                </p>
              </div>
            )}

            {/* Waitlist Info */}
            {teamFormationMode === "waitlist" && (
              <div className="rounded-md border border-muted bg-muted/50 p-4">
                <p className="text-sm text-muted-foreground">
                  You will be added to the waitlist. The system will automatically assign team members or create a solo project after 7 days.
                </p>
              </div>
            )}

            <div className="flex justify-end">
              <Button onClick={handleTeamFormationNext} disabled={loading}>
                Next: Generate Project Idea
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: AI Project Generation */}
      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>Generate Project Idea</CardTitle>
            <CardDescription>AI will generate a project idea based on your team's skills and interests.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {teamMembers.length > 0 && (
              <div className="rounded-md border p-3">
                <p className="text-sm font-medium mb-2">Team Members:</p>
                <div className="flex flex-wrap gap-2">
                  {teamMembers.map((id) => (
                    <Badge key={id} variant="secondary">{id}</Badge>
                  ))}
                </div>
              </div>
            )}
            <Button onClick={generateAiIdeaFromTeam} disabled={loading} className="w-full">
              {loading ? "Generating Project Idea..." : "Generate Project Idea with AI"}
            </Button>
            {aiIdea && (
              <div className="space-y-3 rounded-md border p-4">
                <p className="text-sm font-semibold">{aiIdea.title}</p>
                <p className="text-sm text-muted-foreground">{aiIdea.description}</p>
                {aiIdea.milestones && (
                  <div>
                    <p className="text-xs font-semibold uppercase text-muted-foreground">Milestones</p>
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
                      {aiIdea.milestones.map((milestone, idx) => (
                        <li key={idx}>{milestone}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="flex gap-2 pt-2">
                  <Button onClick={() => setStep(3)} className="flex-1">
                    Use This Idea
                  </Button>
                  <Button onClick={generateAiIdeaFromTeam} variant="outline" disabled={loading}>
                    Generate Another
                  </Button>
                </div>
              </div>
            )}
            <div className="flex justify-between">
              <Button variant="outline" onClick={() => setStep(1)}>
                Back
              </Button>
              {aiIdea && (
                <Button onClick={() => setStep(3)}>
                  Next: Create Project
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Create Project */}
      {step === 3 && (
        <Card>
          <CardHeader>
            <CardTitle>Create Project</CardTitle>
            <CardDescription>Review and finalize your project details. Title and description can be edited or left as AI-generated.</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={createProject}>
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  name="title"
                  value={form.title}
                  onChange={handleChange}
                  placeholder="Project title (required)"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <textarea
                  id="description"
                  name="description"
                  value={form.description}
                  onChange={handleChange}
                  placeholder="Project description (required)"
                  required
                  className="min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>
              {teamMembers.length > 0 && (
                <div className="rounded-md border p-3">
                  <p className="text-sm font-medium mb-2">Team will be assigned:</p>
                  <div className="flex flex-wrap gap-2">
                    {teamMembers.map((id) => (
                      <Badge key={id} variant="secondary">{id}</Badge>
                    ))}
                  </div>
                </div>
              )}
              <div className="flex gap-2">
                <Button type="button" variant="outline" onClick={() => setStep(2)} className="flex-1">
                  Back
                </Button>
                <Button type="submit" disabled={loading} className="flex-1">
                  {loading ? "Creating..." : "Create Project"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

