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
  const [step, setStep] = useState(1); // 1: Team Formation, 2: Domain/Roles, 3: Problem Statement, 4: AI Generation, 5: Task Assignment, 6: Create Project
  const [profile, setProfile] = useState(null);
  const [teamMembers, setTeamMembers] = useState([]);
  const [teamMemberDetails, setTeamMemberDetails] = useState({}); // {user_id: {name, email, role, skills}}
  const [teamFormationMode, setTeamFormationMode] = useState("manual"); // manual, skill_match, interest_match, waitlist
  const [manualMemberId, setManualMemberId] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [searchMode, setSearchMode] = useState("email"); // email, name, user_id
  const [domain, setDomain] = useState(""); // Project domain (e.g., "Web Development", "Data Science")
  const [problemStatement, setProblemStatement] = useState(""); // Clarified problem statement
  const [memberRoles, setMemberRoles] = useState({}); // {user_id: role}
  const [assignedTasks, setAssignedTasks] = useState({}); // {user_id: task}
  const [form, setForm] = useState({ title: "", description: "", ai_generated: false, team_type: "none" });
  const [aiIdea, setAiIdea] = useState(null);
  const [multipleIdeas, setMultipleIdeas] = useState([]); // Store multiple AI-generated ideas
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showWaitlistPrompt, setShowWaitlistPrompt] = useState(false); // Show waitlist prompt when no team found
  const [waitlistData, setWaitlistData] = useState(null); // Store project data when waiting for team

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

  const addMemberFromSearch = async (user) => {
    const userId = user.user_id || user.id;
    if (userId && !teamMembers.includes(userId)) {
      setTeamMembers([...teamMembers, userId]);
      // Store member details
      setTeamMemberDetails((prev) => ({
        ...prev,
        [userId]: {
          name: user.name || userId,
          email: user.email || "",
          skills: user.skills || [],
        },
      }));
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
    // Remove role when member is removed
    setMemberRoles((prev) => {
      const newRoles = { ...prev };
      delete newRoles[memberId];
      return newRoles;
    });
  };

  const generateRoleSuggestions = (domain, teamSize, problemStatement = "") => {
    // Simple role suggestion based on domain and problem statement
    const domainLower = domain.toLowerCase();
    const problemLower = problemStatement.toLowerCase();
    const suggestions = [];
    
    // Check problem statement for additional context
    const needsFrontend = problemLower.includes("ui") || problemLower.includes("interface") || problemLower.includes("user experience") || problemLower.includes("website");
    const needsBackend = problemLower.includes("api") || problemLower.includes("server") || problemLower.includes("database") || problemLower.includes("backend");
    const needsData = problemLower.includes("data") || problemLower.includes("analytics") || problemLower.includes("analysis");
    const needsML = problemLower.includes("machine learning") || problemLower.includes("ml") || problemLower.includes("ai") || problemLower.includes("model");
    
    if (domainLower.includes("web") || domainLower.includes("frontend") || domainLower.includes("backend") || needsFrontend || needsBackend) {
      if (needsFrontend) suggestions.push("Frontend Developer", "UI/UX Designer");
      if (needsBackend) suggestions.push("Backend Developer", "API Developer");
      if (!needsFrontend && !needsBackend) {
        suggestions.push("Frontend Developer", "Backend Developer", "Full Stack Developer", "UI/UX Designer");
      }
    } else if (domainLower.includes("data") || domainLower.includes("science") || domainLower.includes("analytics") || needsData) {
      suggestions.push("Data Scientist", "Data Engineer", "ML Engineer", "Data Analyst");
    } else if (domainLower.includes("mobile") || domainLower.includes("app")) {
      suggestions.push("Mobile Developer", "Backend Developer", "UI/UX Designer", "QA Engineer");
    } else if (domainLower.includes("ai") || domainLower.includes("ml") || domainLower.includes("machine learning") || needsML) {
      suggestions.push("ML Engineer", "Data Scientist", "AI Researcher", "Backend Developer");
    } else {
      suggestions.push("Developer", "Designer", "Engineer", "Specialist");
    }
    
    // Remove duplicates
    const uniqueSuggestions = [...new Set(suggestions)];
    
    // Adjust based on team size
    if (teamSize <= 2) {
      return uniqueSuggestions.slice(0, 2);
    } else if (teamSize <= 4) {
      return uniqueSuggestions.slice(0, 4);
    } else {
      return uniqueSuggestions.slice(0, 5);
    }
  };

  const handleTeamFormationNext = async () => {
    setLoading(true);
    setError("");
    
    try {
      // If skill_match or interest_match, use fully automated AI flow
      if (teamFormationMode === "skill_match" || teamFormationMode === "interest_match") {
        // Use the automated endpoint that does everything
        try {
          const { data } = await apiClient.post("/ai/auto-create-project-with-team", {
            match_mode: teamFormationMode,
            domain: domain || "",
            problem_statement: problemStatement || "",
          }, { timeout: 60000 }).catch(handleApiError); // 60 second timeout for AI operations
          
          if (data) {
            // Check if user needs to decide (no team found)
            if (data.needs_user_decision || (data.matched_count === 0 && !data.project)) {
              // No team members found - show waitlist prompt
              setWaitlistData(data);
              setShowWaitlistPrompt(true);
              setLoading(false);
              return;
            }
            
            // Project and team are already created!
            if (data.project) {
              // Show success message
              if (data.matched_count > 0) {
                setError(`✅ Success! Created team with ${data.team_size} members. ${data.message || ""}`);
              } else {
                setError(`✅ ${data.message || "Project created successfully."}`);
              }
              // Navigate directly to project after a brief delay
              setTimeout(() => {
                navigate(`/projects/${data.project.id}`);
              }, 2000);
              return;
            }
          }
        } catch (autoErr) {
          console.error("Auto-create failed, falling back to manual flow:", autoErr);
          setError(`Auto-create failed: ${autoErr.message}. Trying manual team search...`);
          // Fall back to manual flow if auto-create fails
        }
        
        // Fallback: Manual team member search
        const userSkills = profile?.skills?.map((skill) => skill.name) || [];
        if (userSkills.length === 0) {
          setError("Please add skills to your profile first");
          setLoading(false);
          return;
        }
        
        const skillsQuery = userSkills.join(",");
        const endpoint = teamFormationMode === "skill_match" 
          ? `/users/search/by-skills?skills=${encodeURIComponent(skillsQuery)}&limit=5`
          : `/users/search/by-interests?interests=${encodeURIComponent(skillsQuery)}&limit=5`;
        
        const { data } = await apiClient.get(endpoint, { timeout: 30000 }).catch(handleApiError);
        
        if (data && data.length > 0) {
          // Add top matching users to team with their details
          const newMembers = data.slice(0, 3);
          const newMemberIds = newMembers.map((user) => user.user_id);
          const allMembers = [...teamMembers, ...newMemberIds];
          setTeamMembers(allMembers);
          
          // Store member details
          const newDetails = {};
          newMembers.forEach((user) => {
            newDetails[user.user_id] = {
              name: user.name || user.user_id,
              email: user.email || "",
              skills: user.skills || [],
            };
          });
          setTeamMemberDetails((prev) => ({ ...prev, ...newDetails }));
          
          // Auto-assign roles based on skills
          const roleSuggestions = {};
          newMembers.forEach((user) => {
            const userSkills = (user.skills || []).map(s => s.toLowerCase());
            if (userSkills.some(skill => ["frontend", "react", "vue", "angular", "ui", "design"].some(term => skill.includes(term)))) {
              roleSuggestions[user.user_id] = "Frontend Developer";
            } else if (userSkills.some(skill => ["backend", "server", "api", "database", "node", "python", "java"].some(term => skill.includes(term)))) {
              roleSuggestions[user.user_id] = "Backend Developer";
            } else if (userSkills.some(skill => ["data", "ml", "ai", "analytics", "science"].some(term => skill.includes(term)))) {
              roleSuggestions[user.user_id] = "Data Scientist";
            } else {
              roleSuggestions[user.user_id] = "Team Member";
            }
          });
          setMemberRoles((prev) => ({ ...prev, ...roleSuggestions }));
        } else {
          setError("No matching team members found. Try adding more skills to your profile or use manual team formation.");
        }
      }
      
      if (teamFormationMode === "waitlist") {
        setForm((prev) => ({ ...prev, team_type: "waitlist" }));
        setStep(4); // Skip to AI generation
      } else if (teamMembers.length > 0 || (teamFormationMode === "skill_match" || teamFormationMode === "interest_match")) {
        setForm((prev) => ({ ...prev, team_type: "team" }));
        setStep(2); // Move to domain/role selection
      } else {
        setForm((prev) => ({ ...prev, team_type: "none" }));
        setStep(4); // Skip to AI generation
      }
    } catch (err) {
      setError(err.message || "Failed to find team members. Please try again or use manual team formation.");
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
        domain: domain,
        problem_statement: problemStatement,
        generate_multiple: true, // Generate multiple ideas
      };
      
      const { data } = await apiClient.post("/projects/ai-generate", payload).catch(handleApiError);
      
      // Handle multiple ideas or single idea
      if (data.ideas && data.ideas.length > 0) {
        // Show first idea by default, but allow selection
        setAiIdea(data.ideas[0]);
        setForm((prev) => ({
          ...prev,
          title: data.ideas[0].title || prev.title,
          description: data.ideas[0].description || prev.description,
          ai_generated: true,
        }));
        // Store all ideas for selection
        setMultipleIdeas(data.ideas);
      } else {
        setAiIdea(data);
        setForm((prev) => ({
          ...prev,
          title: data.title || prev.title,
          description: data.description || prev.description,
          ai_generated: true,
        }));
      }
      setStep(5); // Move to task assignment step
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
      
      // ALWAYS include creator as team member and leader (even if no other members)
      const allTeamMembers = teamMembers.includes(user?.id) 
        ? teamMembers 
        : [user?.id, ...teamMembers.filter(id => id !== user?.id)];
      const allRoles = { ...memberRoles };
      if (!allRoles[user?.id]) {
        allRoles[user?.id] = "Team Leader";
      }
      
      // Always create team with creator as member (even for solo projects)
      if (data.id) {
        try {
          await apiClient.post(`/teams/projects/${data.id}/assign-team`, {
            project_id: data.id,
            user_ids: allTeamMembers.length > 0 ? allTeamMembers : [user?.id], // Ensure at least creator
            role_map: allRoles, // Include assigned roles
          });
        } catch (teamErr) {
          console.error("Failed to assign team:", teamErr);
          // Still navigate even if team assignment fails
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
      <div className="flex items-center justify-center gap-2 flex-wrap">
        <div className={`flex items-center gap-1 ${step >= 1 ? "text-primary" : "text-muted-foreground"}`}>
          <div className={`flex h-6 w-6 items-center justify-center rounded-full border-2 text-xs ${step >= 1 ? "border-primary bg-primary text-primary-foreground" : "border-muted"}`}>
            1
          </div>
          <span className="text-xs font-medium hidden sm:inline">Team</span>
        </div>
        <div className={`h-1 w-8 ${step >= 2 ? "bg-primary" : "bg-muted"}`} />
        <div className={`flex items-center gap-1 ${step >= 2 ? "text-primary" : "text-muted-foreground"}`}>
          <div className={`flex h-6 w-6 items-center justify-center rounded-full border-2 text-xs ${step >= 2 ? "border-primary bg-primary text-primary-foreground" : "border-muted"}`}>
            2
          </div>
          <span className="text-xs font-medium hidden sm:inline">Domain/Roles</span>
        </div>
        <div className={`h-1 w-8 ${step >= 3 ? "bg-primary" : "bg-muted"}`} />
        <div className={`flex items-center gap-1 ${step >= 3 ? "text-primary" : "text-muted-foreground"}`}>
          <div className={`flex h-6 w-6 items-center justify-center rounded-full border-2 text-xs ${step >= 3 ? "border-primary bg-primary text-primary-foreground" : "border-muted"}`}>
            3
          </div>
          <span className="text-xs font-medium hidden sm:inline">Problem</span>
        </div>
        <div className={`h-1 w-8 ${step >= 4 ? "bg-primary" : "bg-muted"}`} />
        <div className={`flex items-center gap-1 ${step >= 4 ? "text-primary" : "text-muted-foreground"}`}>
          <div className={`flex h-6 w-6 items-center justify-center rounded-full border-2 text-xs ${step >= 4 ? "border-primary bg-primary text-primary-foreground" : "border-muted"}`}>
            4
          </div>
          <span className="text-xs font-medium hidden sm:inline">AI Idea</span>
        </div>
        <div className={`h-1 w-8 ${step >= 5 ? "bg-primary" : "bg-muted"}`} />
        <div className={`flex items-center gap-1 ${step >= 5 ? "text-primary" : "text-muted-foreground"}`}>
          <div className={`flex h-6 w-6 items-center justify-center rounded-full border-2 text-xs ${step >= 5 ? "border-primary bg-primary text-primary-foreground" : "border-muted"}`}>
            5
          </div>
          <span className="text-xs font-medium hidden sm:inline">Tasks</span>
        </div>
        <div className={`h-1 w-8 ${step >= 6 ? "bg-primary" : "bg-muted"}`} />
        <div className={`flex items-center gap-1 ${step >= 6 ? "text-primary" : "text-muted-foreground"}`}>
          <div className={`flex h-6 w-6 items-center justify-center rounded-full border-2 text-xs ${step >= 6 ? "border-primary bg-primary text-primary-foreground" : "border-muted"}`}>
            6
          </div>
          <span className="text-xs font-medium hidden sm:inline">Create</span>
        </div>
      </div>

      {error ? <p className="text-sm text-destructive text-center">{error}</p> : null}
      
      {/* Waitlist Prompt Modal */}
      {showWaitlistPrompt && waitlistData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
          <Card className="max-w-md w-full mx-4">
            <CardHeader>
              <CardTitle>No Team Members Found</CardTitle>
              <CardDescription>
                We couldn't find any matching team members right now. Would you like to wait for 7 days while we search for compatible teammates?
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-md border border-primary/20 bg-primary/5 p-3">
                <p className="text-sm font-medium mb-1">⏰ Waitlist Option:</p>
                <p className="text-xs text-muted-foreground">
                  • We'll search for compatible team members for 7 days<br/>
                  • If no team is found within 7 days, a solo project will be created automatically<br/>
                  • You can start working on the project immediately
                </p>
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={async () => {
                    setLoading(true);
                    try {
                      // Create project with waitlist
                      const { data } = await apiClient.post("/ai/auto-create-project-with-team", {
                        match_mode: teamFormationMode,
                        domain: domain || "",
                        problem_statement: problemStatement || "",
                        wait_for_team: true, // User wants to wait
                      }, { timeout: 60000 }).catch(handleApiError);
                      
                      if (data && data.project) {
                        setError(`✅ ${data.message || "You've been added to the waitlist. We'll notify you when team members are found."}`);
                        setTimeout(() => {
                          navigate(`/projects/${data.project.id}`);
                        }, 2000);
                      }
                    } catch (err) {
                      setError(`Failed to create waitlist project: ${err.message}`);
                    } finally {
                      setLoading(false);
                      setShowWaitlistPrompt(false);
                    }
                  }}
                  disabled={loading}
                  className="flex-1"
                >
                  {loading ? "Creating..." : "Yes, Wait for Team"}
                </Button>
                <Button
                  onClick={async () => {
                    setLoading(true);
                    try {
                      // Create solo project immediately
                      const { data } = await apiClient.post("/ai/auto-create-project-with-team", {
                        match_mode: teamFormationMode,
                        domain: domain || "",
                        problem_statement: problemStatement || "",
                        wait_for_team: false, // User doesn't want to wait
                      }, { timeout: 60000 }).catch(handleApiError);
                      
                      if (data && data.project) {
                        setError(`✅ ${data.message || "Solo project created successfully."}`);
                        setTimeout(() => {
                          navigate(`/projects/${data.project.id}`);
                        }, 2000);
                      }
                    } catch (err) {
                      setError(`Failed to create solo project: ${err.message}`);
                    } finally {
                      setLoading(false);
                      setShowWaitlistPrompt(false);
                    }
                  }}
                  variant="outline"
                  disabled={loading}
                  className="flex-1"
                >
                  {loading ? "Creating..." : "No, Create Solo Project"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

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
              <div className="rounded-md border border-primary/20 bg-primary/5 p-4">
                <p className="text-sm font-medium text-primary mb-1">
                  🤖 AI-Powered Team Formation
                </p>
                <p className="text-sm text-muted-foreground">
                  AI will automatically find matching team members, assign roles, generate a project idea, and create the project - all in one click!
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  No manual steps needed. Just click "AI: Find Team & Create Project" and AI will handle everything.
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
                {teamFormationMode === "skill_match" || teamFormationMode === "interest_match" 
                  ? (loading ? "AI is working..." : "🤖 AI: Find Team & Create Project")
                  : teamMembers.length > 0 
                  ? "Next: Domain & Roles" 
                  : "Next: Generate Project Idea"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Domain & Role Selection */}
      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>Domain & Team Roles</CardTitle>
            <CardDescription>Specify the project domain and assign roles to each team member. AI will suggest roles based on domain and team size.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="domain">Project Domain</Label>
              <Input
                id="domain"
                placeholder="e.g., Web Development, Data Science, Mobile App, AI/ML, etc."
                value={domain}
                onChange={async (e) => {
                  setDomain(e.target.value);
                  // Auto-suggest roles when domain is entered and we have team members
                  if (e.target.value.trim() && teamMembers.length > 0) {
                    try {
                      // Generate role suggestions based on domain and team size
                      const teamSize = teamMembers.length + 1; // Include creator
                      const roles = generateRoleSuggestions(e.target.value, teamSize);
                      setSuggestedRoles(roles);
                    } catch (err) {
                      console.error("Failed to generate role suggestions:", err);
                    }
                  }
                }}
              />
              <p className="text-xs text-muted-foreground">
                The domain helps AI generate appropriate project ideas and assign relevant tasks.
              </p>
            </div>

            {suggestedRoles.length > 0 && (
              <div className="rounded-md border p-3 bg-muted/50">
                <p className="text-sm font-medium mb-2">AI Suggested Roles:</p>
                <div className="flex flex-wrap gap-2">
                  {suggestedRoles.map((role, idx) => (
                    <Badge key={idx} variant="secondary">{role}</Badge>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  These roles are suggested based on your project domain and team size ({teamMembers.length + 1} members).
                </p>
              </div>
            )}

            <div className="space-y-3">
              <Label>Assign Roles to Team Members</Label>
              {/* Creator (always Team Leader) */}
              <div className="rounded-md border p-3 space-y-2 bg-primary/5">
                <div>
                  <p className="font-medium">You (Creator)</p>
                  <p className="text-xs text-muted-foreground">{user?.email || user?.id}</p>
                </div>
                <Input
                  value={memberRoles[user?.id] || "Team Leader"}
                  onChange={(e) => setMemberRoles((prev) => ({ ...prev, [user?.id]: e.target.value }))}
                  disabled
                  className="bg-background"
                />
                <p className="text-xs text-muted-foreground">You are automatically the Team Leader</p>
              </div>

              {/* Other team members */}
              {teamMembers.filter(id => id !== user?.id).map((memberId) => {
                const memberInfo = teamMemberDetails[memberId] || { name: memberId, skills: [] };
                return (
                  <div key={memberId} className="rounded-md border p-3 space-y-2">
                    <div>
                      <p className="font-medium">{memberInfo.name}</p>
                      <p className="text-xs text-muted-foreground">{memberInfo.email || memberId}</p>
                      {memberInfo.skills && memberInfo.skills.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {memberInfo.skills.slice(0, 5).map((skill, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">{skill}</Badge>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Input
                        placeholder="Select or enter role"
                        value={memberRoles[memberId] || ""}
                        onChange={(e) => setMemberRoles((prev) => ({ ...prev, [memberId]: e.target.value }))}
                        list={`roles-${memberId}`}
                      />
                      {suggestedRoles.length > 0 && (
                        <datalist id={`roles-${memberId}`}>
                          {suggestedRoles.filter(r => r !== "Team Leader").map((role) => (
                            <option key={role} value={role} />
                          ))}
                        </datalist>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="flex justify-between">
              <Button variant="outline" onClick={() => setStep(1)}>
                Back
              </Button>
              <Button onClick={() => setStep(3)} disabled={!domain.trim()}>
                Next: Problem Statement
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Problem Statement */}
      {step === 3 && (
        <Card>
          <CardHeader>
            <CardTitle>Clarify Problem Statement</CardTitle>
            <CardDescription>Describe the problem you want to solve or the goal of this project. This will help refine role suggestions.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="problemStatement">Problem Statement / Project Goal</Label>
              <textarea
                id="problemStatement"
                placeholder="Describe what problem this project will solve, what goals you want to achieve, or what you want to build..."
                value={problemStatement}
                onChange={(e) => {
                  setProblemStatement(e.target.value);
                  // Update role suggestions when problem statement changes
                  if (domain && e.target.value.trim() && teamMembers.length > 0) {
                    const teamSize = teamMembers.length + 1;
                    const roles = generateRoleSuggestions(domain, teamSize, e.target.value);
                    setSuggestedRoles(roles);
                  }
                }}
                className="min-h-[150px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
              <p className="text-xs text-muted-foreground">
                This helps AI generate a more targeted project idea and assign appropriate tasks and roles.
              </p>
            </div>

            {domain && (
              <div className="rounded-md border p-3">
                <p className="text-sm font-medium">Domain: {domain}</p>
              </div>
            )}

            {suggestedRoles.length > 0 && (
              <div className="rounded-md border p-3 bg-muted/50">
                <p className="text-sm font-medium mb-2">Updated AI Suggested Roles:</p>
                <div className="flex flex-wrap gap-2">
                  {suggestedRoles.map((role, idx) => (
                    <Badge key={idx} variant="secondary">{role}</Badge>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Roles updated based on domain and problem statement.
                </p>
              </div>
            )}

            <div className="flex justify-between">
              <Button variant="outline" onClick={() => setStep(2)}>
                Back
              </Button>
              <Button onClick={() => setStep(4)}>
                Next: Generate Project Idea
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 4: AI Project Generation */}
      {step === 4 && (
        <Card>
          <CardHeader>
            <CardTitle>Generate Project Idea</CardTitle>
            <CardDescription>AI will generate a project idea based on your team's skills, domain, and problem statement.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {teamMembers.length > 0 && (
              <div className="rounded-md border p-3">
                <p className="text-sm font-medium mb-2">Team Members ({teamMembers.length}):</p>
                <div className="flex flex-wrap gap-2">
                  {teamMembers.map((id) => {
                    const memberInfo = teamMemberDetails[id] || { name: id };
                    return (
                      <Badge key={id} variant="secondary">
                        {memberInfo.name} {memberRoles[id] ? `(${memberRoles[id]})` : ""}
                      </Badge>
                    );
                  })}
                </div>
              </div>
            )}
            {domain && (
              <div className="rounded-md border p-3">
                <p className="text-sm font-medium">Domain: {domain}</p>
              </div>
            )}
            {problemStatement && (
              <div className="rounded-md border p-3">
                <p className="text-sm font-medium mb-1">Problem Statement:</p>
                <p className="text-sm text-muted-foreground">{problemStatement}</p>
              </div>
            )}
            <Button onClick={generateAiIdeaFromTeam} disabled={loading} className="w-full">
              {loading ? "Generating Project Idea..." : "Generate Project Idea with AI"}
            </Button>
            {multipleIdeas.length > 0 && (
              <div className="space-y-3">
                <p className="text-sm font-medium">Select a project idea:</p>
                {multipleIdeas.map((idea, idx) => (
                  <div
                    key={idx}
                    className={`rounded-md border p-3 cursor-pointer transition-colors ${
                      aiIdea?.title === idea.title ? "border-primary bg-primary/5" : "border-muted hover:bg-muted/50"
                    }`}
                    onClick={() => {
                      setAiIdea(idea);
                      setForm((prev) => ({
                        ...prev,
                        title: idea.title || prev.title,
                        description: idea.description || prev.description,
                        ai_generated: true,
                      }));
                    }}
                  >
                    <p className="text-sm font-semibold">{idea.title}</p>
                    <p className="text-sm text-muted-foreground">{idea.description}</p>
                  </div>
                ))}
              </div>
            )}
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
                  <Button onClick={() => setStep(5)} className="flex-1">
                    Use This Idea
                  </Button>
                  <Button onClick={generateAiIdeaFromTeam} variant="outline" disabled={loading}>
                    Generate More Ideas
                  </Button>
                </div>
              </div>
            )}
            <div className="flex justify-between">
              <Button variant="outline" onClick={() => setStep(problemStatement ? 3 : 2)}>
                Back
              </Button>
              {aiIdea && (
                <Button onClick={() => setStep(5)}>
                  Next: Assign Tasks
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 5: AI Task Assignment */}
      {step === 5 && (
        <Card>
          <CardHeader>
            <CardTitle>AI Task Assignment</CardTitle>
            <CardDescription>AI will assign specific tasks to each team member based on their roles and skills.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {aiIdea && (
              <div className="rounded-md border p-3 mb-4">
                <p className="text-sm font-semibold mb-1">Project: {aiIdea.title}</p>
                <p className="text-xs text-muted-foreground">{aiIdea.description}</p>
              </div>
            )}
            <Button
              onClick={async () => {
                setLoading(true);
                try {
                  // Generate tasks for each team member
                  const tasks = {};
                  for (const memberId of teamMembers) {
                    const memberInfo = teamMemberDetails[memberId] || {};
                    const role = memberRoles[memberId] || "Team Member";
                    const skills = memberInfo.skills || [];
                    
                    // Call AI to generate task for this member
                    const taskPrompt = `Generate a specific task for a ${role} with skills: ${skills.join(", ")}. 
                    Project: ${aiIdea?.title || form.title}
                    Domain: ${domain}
                    Problem: ${problemStatement}
                    Provide a clear, actionable task description.`;
                    
                    try {
                      const { data } = await apiClient.post("/ai/assistant-chat", {
                        project_id: null,
                        user_id: user?.id,
                        message: taskPrompt,
                      }).catch(handleApiError);
                      
                      tasks[memberId] = data.response || `Work on ${role} tasks for the project`;
                    } catch {
                      tasks[memberId] = `Work on ${role} tasks for the project`;
                    }
                  }
                  setAssignedTasks(tasks);
                } catch (err) {
                  setError("Failed to assign tasks. You can proceed without task assignment.");
                } finally {
                  setLoading(false);
                }
              }}
              disabled={loading}
              className="w-full"
            >
              {loading ? "Assigning Tasks..." : "Generate Tasks with AI"}
            </Button>

            {Object.keys(assignedTasks).length > 0 && (
              <div className="space-y-3">
                <p className="text-sm font-medium">Assigned Tasks:</p>
                {teamMembers.map((memberId) => {
                  const memberInfo = teamMemberDetails[memberId] || { name: memberId };
                  const task = assignedTasks[memberId];
                  return (
                    <div key={memberId} className="rounded-md border p-3">
                      <p className="font-medium text-sm">{memberInfo.name}</p>
                      <p className="text-xs text-muted-foreground mb-2">
                        Role: {memberRoles[memberId] || "Team Member"}
                      </p>
                      <p className="text-sm">{task}</p>
                    </div>
                  );
                })}
              </div>
            )}

            <div className="flex justify-between">
              <Button variant="outline" onClick={() => setStep(4)}>
                Back
              </Button>
              <Button onClick={() => setStep(6)}>
                Next: Create Project
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 6: Create Project */}
      {step === 6 && (
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
              {teamMembers.length > 0 && (
                <div className="rounded-md border p-3">
                  <p className="text-sm font-medium mb-2">Team Members ({teamMembers.length}):</p>
                  <div className="space-y-2">
                    {teamMembers.map((memberId) => {
                      const memberInfo = teamMemberDetails[memberId] || { name: memberId };
                      const role = memberRoles[memberId];
                      const task = assignedTasks[memberId];
                      return (
                        <div key={memberId} className="text-sm">
                          <p className="font-medium">{memberInfo.name} {role && <span className="text-muted-foreground">({role})</span>}</p>
                          {task && <p className="text-xs text-muted-foreground">Task: {task}</p>}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
              <div className="flex gap-2">
                <Button type="button" variant="outline" onClick={() => setStep(5)} className="flex-1">
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

