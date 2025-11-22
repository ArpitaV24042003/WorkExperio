import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";

// Simple inline charts using div bars to avoid adding extra chart deps if not desired elsewhere

function ProgressBar({ value }) {
  const pct = Math.max(0, Math.min(100, Number.isFinite(value) ? value : 0));
  return (
    <div className="w-full bg-muted rounded-full h-2">
      <div
        className="bg-primary h-2 rounded-full transition-all"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

function MiniBarChart({ data }) {
  if (!data?.length) {
    return <p className="text-xs text-muted-foreground">No data yet.</p>;
  }
  const max = Math.max(...data.map((d) => d.value || 0), 1);
  return (
    <div className="flex items-end gap-1 h-20">
      {data.map((d) => (
        <div key={d.label} className="flex-1 flex flex-col items-center gap-1">
          <div
            className="w-full bg-primary/70 rounded-t-sm"
            style={{ height: `${(d.value / max) * 100}%` }}
          />
          <span className="text-[10px] text-muted-foreground truncate w-full text-center">
            {d.label}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function ProjectsDashboard() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const [project, setProject] = useState(null);
  const [members, setMembers] = useState([]);
  const [memberDetails, setMemberDetails] = useState({}); // user_id -> { name, email }
  const [analytics, setAnalytics] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [files, setFiles] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [newMemberId, setNewMemberId] = useState("");
  const [updatingMember, setUpdatingMember] = useState(false);

  const [taskForm, setTaskForm] = useState({
    title: "",
    description: "",
    estimated_hours: "",
    assignee_id: "",
    due_date: "",
  });
  const [creatingTask, setCreatingTask] = useState(false);

  const [chatMessage, setChatMessage] = useState("");
  const [sendingChat, setSendingChat] = useState(false);

  const [uploadingFile, setUploadingFile] = useState(false);
  const [aiAssigning, setAiAssigning] = useState(false);
  const [aiGeneratingTasks, setAiGeneratingTasks] = useState(false);
  const [aiPlan, setAiPlan] = useState(null);
  const [suggestedRoles, setSuggestedRoles] = useState([]);
  const [activePanel, setActivePanel] = useState(null); // "team" | "tasks" | "files" | "analytics" | "ai" | null
  const [analyzingCode, setAnalyzingCode] = useState(false);
  const [codeAnalysisResult, setCodeAnalysisResult] = useState(null);

  const isOwner = project && user?.id && project.owner_id === user.id;

  const currentUserTasks = useMemo(
    () => tasks.filter((t) => t.assignee_id === user?.id),
    [tasks, user?.id]
  );

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      setError("");
      try {
        const [projectRes, membersRes, analyticsRes, tasksRes, filesRes, chatRes] =
          await Promise.all([
            apiClient.get(`/projects/${projectId}`).catch(handleApiError),
            apiClient.get(`/projects/${projectId}/members`).catch(handleApiError),
            apiClient
              .get(`/projects/${projectId}/analytics/overview`)
              .catch(handleApiError),
            apiClient
              .get(`/projects/${projectId}/tasks`)
              .catch(handleApiError),
            apiClient
              .get(`/projects/${projectId}/files`)
              .catch(handleApiError),
            apiClient
              .get(`/projects/${projectId}/ai/history`)
              .catch(handleApiError),
          ]);

        setProject(projectRes?.data || null);
        setMembers(membersRes?.data?.members || []);
        setAnalytics(analyticsRes?.data || null);
        setTasks(tasksRes?.data || []);
        setFiles(filesRes?.data || []);
        setChatHistory(chatRes?.data || []);
      } catch (err) {
        console.error("Dashboard load error:", err);
        setError(err.message || "Failed to load project dashboard.");
      } finally {
        setLoading(false);
      }
    };
    if (projectId) {
      loadAll();
    }
  }, [projectId]);

  // Load friendly display names for members so we don't show raw UUIDs in UI.
  useEffect(() => {
    const loadMemberDetails = async () => {
      if (!members.length) return;

      const current = { ...memberDetails };
      const missing = members
        .map((m) => m.user_id)
        .filter((id) => id && !current[id]);
      if (!missing.length) return;

      try {
        const updates = {};
        for (const id of missing) {
          try {
            const res = await apiClient
              .get(`/users/${id}/profile`)
              .catch(() => null);
            if (res?.data) {
              updates[id] = {
                name: res.data.name || id,
                email: res.data.email || "",
              };
            } else {
              updates[id] = { name: id, email: "" };
            }
          } catch {
            updates[id] = { name: id, email: "" };
          }
        }
        setMemberDetails((prev) => ({ ...prev, ...updates }));
      } catch (err) {
        console.error("Failed to load member details:", err);
      }
    };

    loadMemberDetails();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [members]);

  const getMemberName = (userId) => {
    if (!userId) return "";
    return memberDetails[userId]?.name || userId.slice(0, 8);
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!taskForm.title.trim()) return;
    setCreatingTask(true);
    try {
      const payload = {
        title: taskForm.title.trim(),
        description: taskForm.description || null,
        estimated_hours: taskForm.estimated_hours
          ? Number(taskForm.estimated_hours)
          : null,
        assignee_id: taskForm.assignee_id || null,
        due_date: taskForm.due_date || null,
      };
      const { data } = await apiClient
        .post(`/projects/${projectId}/tasks`, payload)
        .catch(handleApiError);
      setTasks((prev) => [...prev, data]);
      setTaskForm({
        title: "",
        description: "",
        estimated_hours: "",
        assignee_id: "",
        due_date: "",
      });
    } catch (err) {
      console.error("Create task error:", err);
      alert(err.message || "Failed to create task.");
    } finally {
      setCreatingTask(false);
    }
  };

  const updateTaskStatus = async (taskId, updates) => {
    try {
      const { data } = await apiClient
        .patch(`/projects/${projectId}/tasks/${taskId}`, updates)
        .catch(handleApiError);
      setTasks((prev) => prev.map((t) => (t.id === taskId ? data : t)));
    } catch (err) {
      console.error("Update task error:", err);
      const errorMessage = err.message || "Failed to update task.";
      // Check if it's a validation error
      if (errorMessage.includes("validation failed")) {
        alert(`Task validation failed: ${errorMessage}\n\nPlease ensure the task requirements are met before marking as complete.`);
      } else {
        alert(errorMessage);
      }
    }
  };

  const handleStartTimer = async (taskId) => {
    try {
      await apiClient
        .post(`/tasks/${taskId}/timelogs/start`)
        .catch(handleApiError);
      // No UI for active timer list; rely on analytics
      alert("Timer started for this task.");
    } catch (err) {
      console.error("Start timelog error:", err);
      alert(err.message || "Failed to start timer.");
    }
  };

  const handleStopTimer = async (taskId) => {
    try {
      await apiClient
        .post(`/tasks/${taskId}/timelogs/stop`)
        .catch(handleApiError);
      alert("Timer stopped for this task.");
    } catch (err) {
      console.error("Stop timelog error:", err);
      alert(err.message || "Failed to stop timer.");
    }
  };

  const handleAddMember = async () => {
    if (!newMemberId.trim()) return;
    setUpdatingMember(true);
    try {
      const { data } = await apiClient
        .post(`/projects/${projectId}/members`, { user_id: newMemberId.trim() })
        .catch(handleApiError);
      if (data?.member) {
        setMembers((prev) => [...prev, data.member]);
        setNewMemberId("");
      }
    } catch (err) {
      console.error("Add member error:", err);
      alert(err.message || "Failed to add member.");
    } finally {
      setUpdatingMember(false);
    }
  };

  const handleChangeRole = async (memberUserId, role) => {
    if (!role.trim()) return;
    try {
      const { data } = await apiClient
        .patch(`/projects/${projectId}/members/${memberUserId}/role`, {
          role: role.trim(),
        })
        .catch(handleApiError);
      if (data?.member) {
        setMembers((prev) =>
          prev.map((m) =>
            m.user_id === memberUserId ? { ...m, role: data.member.role } : m
          )
        );
      }
    } catch (err) {
      console.error("Update role error:", err);
      alert(err.message || "Failed to update role.");
    }
  };

  const handleSendChat = async (e) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;
    setSendingChat(true);
    try {
      const { data } = await apiClient
        .post(`/projects/${projectId}/ai/chat`, { message: chatMessage.trim() })
        .catch(handleApiError);
      setChatMessage("");
      // Reload history
      const history = await apiClient
        .get(`/projects/${projectId}/ai/history`)
        .catch(handleApiError);
      setChatHistory(history?.data || []);
      if (data?.reply) {
        // no-op; reply is already in history
      }
    } catch (err) {
      console.error("Chat error:", err);
      alert(err.message || "Failed to send message.");
    } finally {
      setSendingChat(false);
    }
  };

  const handleUploadFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingFile(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await apiClient
        .post(`/projects/${projectId}/files`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        })
        .catch(handleApiError);
      if (data) {
        const { data: list } = await apiClient
          .get(`/projects/${projectId}/files`)
          .catch(handleApiError);
        setFiles(list || []);
      }
    } catch (err) {
      console.error("Upload error:", err);
      alert(err.message || "Failed to upload file.");
    } finally {
      setUploadingFile(false);
      e.target.value = "";
    }
  };

  const handleDeleteProject = async () => {
    if (!project) return;
    if (!window.confirm("Are you sure you want to delete this project?")) {
      return;
    }
    try {
      await apiClient
        .delete(`/projects/${project.id}`)
        .catch(handleApiError);
      navigate("/projects");
    } catch (err) {
      console.error("Delete project error:", err);
      alert(err.message || "Failed to delete project.");
    }
  };

  const handleSuggestRoles = async () => {
    if (!projectId) return;
    try {
      const { data } = await apiClient
        .post(`/teams/projects/${projectId}/suggest-roles`)
        .catch(handleApiError);
      const roles = data?.suggested_roles || [];
      setSuggestedRoles(roles);

      // Auto-assign suggested roles to members (zip by index)
      if (roles.length && members.length) {
        await Promise.all(
          members.map((m, idx) => {
            const role = roles[idx % roles.length];
            return apiClient
              .patch(`/projects/${projectId}/members/${m.user_id}/role`, {
                role,
              })
              .catch(handleApiError);
          })
        );
        // Refresh members list
        const refreshed = await apiClient
          .get(`/projects/${projectId}/members`)
          .catch(handleApiError);
        setMembers(refreshed?.data?.members || []);
      }
    } catch (err) {
      console.error("Suggest roles error:", err);
      alert(err.message || "Failed to suggest roles.");
    }
  };

  const handleRunAiAssign = async () => {
    if (!projectId) return;
    setAiAssigning(true);
    try {
      const { data } = await apiClient
        .post(`/projects/${projectId}/ai-assign`)
        .catch(handleApiError);
      setAiPlan(data || null);
      if (data?.assignments?.length) {
        // Refresh tasks to reflect new assignees / due dates
        const { data: refreshed } = await apiClient
          .get(`/projects/${projectId}/tasks`)
          .catch(handleApiError);
        setTasks(refreshed || []);
      }
      setActivePanel("tasks");
    } catch (err) {
      console.error("AI assign error:", err);
      alert(err.message || "Failed to run AI assignment.");
    } finally {
      setAiAssigning(false);
    }
  };

  const handleGenerateTasks = async () => {
    if (!projectId) return;
    setAiGeneratingTasks(true);
    try {
      const { data } = await apiClient
        .post(`/projects/${projectId}/ai-generate-tasks`)
        .catch(handleApiError);
      if (data && data.length > 0) {
        setTasks((prev) => [...prev, ...data]);
        alert(`Successfully generated ${data.length} tasks!`);
        setActivePanel("tasks");
      } else {
        alert("No new tasks were generated. Tasks may already exist for this project.");
      }
    } catch (err) {
      console.error("AI generate tasks error:", err);
      alert(err.message || "Failed to generate tasks.");
    } finally {
      setAiGeneratingTasks(false);
    }
  };

  const handleAnalyzeCode = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAnalyzingCode(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("analysis_type", "comprehensive");
      const { data } = await apiClient
        .post(`/projects/${projectId}/analyze-code`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        })
        .catch(handleApiError);
      setCodeAnalysisResult(data);
      alert(`Code analysis complete! Score: ${data.score?.toFixed(1)}/100`);
    } catch (err) {
      console.error("Code analysis error:", err);
      alert(err.message || "Failed to analyze code.");
    } finally {
      setAnalyzingCode(false);
      e.target.value = "";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <p className="text-sm text-muted-foreground">Loading project dashboard...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-3">
        <p className="text-sm text-destructive">
          {error || "Project not found or you do not have access."}
        </p>
        <Button variant="outline" onClick={() => navigate("/projects")}>
          Back to Projects
        </Button>
      </div>
    );
  }

  const memberHoursData =
    analytics?.members?.map((m) => ({
      label: getMemberName(m.user_id) || m.user_id.slice(0, 6),
      value: m.total_hours,
    })) || [];

  const timelineData =
    analytics?.timeline?.map((t) => ({
      label: t.date.slice(5),
      value: t.completed_count,
    })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-semibold">{project.title}</h1>
          <p className="text-muted-foreground">{project.description}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Project ID: <code className="font-mono">{project.id}</code>
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline">Owner: {getMemberName(project.owner_id)}</Badge>
          <Badge variant="outline">Team: {project.team_type}</Badge>
          {isOwner && (
            <Button variant="destructive" size="sm" onClick={handleDeleteProject}>
              Delete
            </Button>
          )}
        </div>
      </div>

      {/* Overview cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6">
        <Card>
          <CardHeader>
            <CardTitle>Team Members</CardTitle>
            <CardDescription>Roles and access for this project.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-2xl font-semibold">{members.length}</p>
            <p className="text-xs text-muted-foreground">members in team</p>
            <Button size="sm" variant="outline" onClick={() => setActivePanel("team")}>
              View Details
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Tasks</CardTitle>
            <CardDescription>Backlog and current work.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-2xl font-semibold">{tasks.length}</p>
            <p className="text-xs text-muted-foreground">
              {analytics?.tasks_completed ?? 0} completed
            </p>
            <Button size="sm" variant="outline" onClick={() => setActivePanel("tasks")}>
              View Details
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Files</CardTitle>
            <CardDescription>Uploads and artifacts.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-2xl font-semibold">{files.length}</p>
            <p className="text-xs text-muted-foreground">project files</p>
            <Button size="sm" variant="outline" onClick={() => setActivePanel("files")}>
              View Details
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Analytics</CardTitle>
            <CardDescription>Completion and performance.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-2xl font-semibold">
              {analytics?.percent_complete?.toFixed(0) ?? 0}%
            </p>
            <p className="text-xs text-muted-foreground">overall completion</p>
            <Button
              size="sm"
              variant="outline"
              onClick={() => navigate(`/projects/${projectId}/performance`)}
            >
              Open Analytics
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Assistant</CardTitle>
            <CardDescription>Chat and task guidance.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-2xl font-semibold">
              {chatHistory.length}
            </p>
            <p className="text-xs text-muted-foreground">messages in this project</p>
            <Button
              size="sm"
              variant="outline"
              onClick={() => navigate(`/projects/${projectId}/assistant`)}
            >
              Open Assistant
            </Button>
          </CardContent>
        </Card>

        {project?.team_id && (
          <Card>
            <CardHeader>
              <CardTitle>Team Chat</CardTitle>
              <CardDescription>Real-time team communication.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-2xl font-semibold">
                {members.length}
              </p>
              <p className="text-xs text-muted-foreground">team members</p>
              <Button
                size="sm"
                variant="outline"
                onClick={() => navigate(`/projects/${projectId}/chat`)}
              >
                Open Chat
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Detailed panels */}
      {activePanel === "team" && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between gap-2">
            <div>
              <CardTitle>Team Members</CardTitle>
              <CardDescription>
                Manage roles and invite known members using their User ID.
              </CardDescription>
            </div>
            <div className="flex gap-2">
              {isOwner && (
                <Button size="sm" variant="outline" onClick={handleSuggestRoles}>
                  AI Suggest Roles
                </Button>
              )}
              <Button size="sm" variant="ghost" onClick={() => setActivePanel(null)}>
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {isOwner && (
              <div className="space-y-2">
                <Label htmlFor="member-id">Add member by User ID</Label>
                <div className="flex gap-2">
                  <Input
                    id="member-id"
                    placeholder="UUID from Profile page"
                    value={newMemberId}
                    onChange={(e) => setNewMemberId(e.target.value)}
                  />
                  <Button
                    size="sm"
                    onClick={handleAddMember}
                    disabled={updatingMember || !newMemberId.trim()}
                  >
                    {updatingMember ? "Adding..." : "Add"}
                  </Button>
                </div>
              </div>
            )}
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {members.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No members yet. Add known members using their User ID from Profile.
                </p>
              ) : (
                members.map((m) => (
                  <div
                    key={m.id}
                    className="space-y-1 rounded-md border p-2 text-sm"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{getMemberName(m.user_id)}</span>
                      {project.owner_id === m.user_id && (
                        <Badge variant="secondary">Owner</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-muted-foreground">Role:</span>
                      {user?.id === m.user_id || isOwner ? (
                        suggestedRoles.length ? (
                          <select
                            className="h-7 text-xs rounded border bg-background px-1"
                            value={m.role || ""}
                            onChange={(e) => handleChangeRole(m.user_id, e.target.value || "")}
                          >
                            <option value="">Select role</option>
                            {suggestedRoles.map((role) => (
                              <option key={role} value={role}>
                                {role}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <Input
                            className="h-7 text-xs"
                            defaultValue={m.role || ""}
                            placeholder="Set role"
                            onBlur={(e) =>
                              handleChangeRole(m.user_id, e.target.value || "")
                            }
                          />
                        )
                      ) : (
                        <span className="text-xs">
                          {m.role || (
                            <span className="italic text-muted-foreground">Pending</span>
                          )}
                        </span>
                      )}
                    </div>
                    {m.task && (
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        Task: {m.task}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {activePanel === "tasks" && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between gap-2">
            <div>
              <CardTitle>Tasks</CardTitle>
              <CardDescription>Create and track work items with timers.</CardDescription>
            </div>
            <div className="flex gap-2">
              {isOwner && (
                <>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleGenerateTasks}
                    disabled={aiGeneratingTasks}
                  >
                    {aiGeneratingTasks ? "Generating..." : "AI Generate Tasks"}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleRunAiAssign}
                    disabled={aiAssigning}
                  >
                    {aiAssigning ? "Assigning..." : "AI Assign Roles & Schedule"}
                  </Button>
                </>
              )}
              <Button size="sm" variant="ghost" onClick={() => setActivePanel(null)}>
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <form className="space-y-2" onSubmit={handleCreateTask}>
              <div className="grid gap-2 md:grid-cols-2">
                <div className="space-y-1">
                  <Label htmlFor="task-title">Title</Label>
                  <Input
                    id="task-title"
                    value={taskForm.title}
                    onChange={(e) =>
                      setTaskForm((prev) => ({ ...prev, title: e.target.value }))
                    }
                    placeholder="Task title"
                    required
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="task-assignee">Assignee ID (optional)</Label>
                  <Input
                    id="task-assignee"
                    value={taskForm.assignee_id}
                    onChange={(e) =>
                      setTaskForm((prev) => ({
                        ...prev,
                        assignee_id: e.target.value,
                      }))
                    }
                    placeholder="User ID"
                  />
                </div>
              </div>
              <div className="grid gap-2 md:grid-cols-3">
                <div className="space-y-1 md:col-span-2">
                  <Label htmlFor="task-desc">Description</Label>
                  <Input
                    id="task-desc"
                    value={taskForm.description}
                    onChange={(e) =>
                      setTaskForm((prev) => ({
                        ...prev,
                        description: e.target.value,
                      }))
                    }
                    placeholder="Short description"
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="task-hours">Est. hours</Label>
                  <Input
                    id="task-hours"
                    type="number"
                    min="0"
                    step="0.5"
                    value={taskForm.estimated_hours}
                    onChange={(e) =>
                      setTaskForm((prev) => ({
                        ...prev,
                        estimated_hours: e.target.value,
                      }))
                    }
                  />
                </div>
              </div>
              <div className="grid gap-2 md:grid-cols-2 items-end">
                <div className="space-y-1">
                  <Label htmlFor="task-due">Due date</Label>
                  <Input
                    id="task-due"
                    type="datetime-local"
                    value={taskForm.due_date}
                    onChange={(e) =>
                      setTaskForm((prev) => ({
                        ...prev,
                        due_date: e.target.value,
                      }))
                    }
                  />
                </div>
                <div className="flex justify-end">
                  <Button type="submit" disabled={creatingTask}>
                    {creatingTask ? "Creating..." : "Add Task"}
                  </Button>
                </div>
              </div>
            </form>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium">All Tasks</h3>
                <span className="text-xs text-muted-foreground">
                  {tasks.length} total
                </span>
              </div>
              {tasks.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No tasks yet. Create one to get started.
                </p>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {tasks.map((t) => (
                    <div
                      key={t.id}
                      className="rounded-md border p-2 flex flex-col gap-1 text-sm"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <p className="font-medium">{t.title}</p>
                        <div className="flex items-center gap-1">
                          <Badge
                            variant={
                              t.status === "done"
                                ? "success"
                                : t.status === "in_progress"
                                ? "secondary"
                                : "outline"
                            }
                          >
                            {t.status}
                          </Badge>
                          <input
                            type="checkbox"
                            className="h-4 w-4"
                            checked={t.status === "done"}
                            onChange={(e) =>
                              updateTaskStatus(t.id, {
                                status: e.target.checked ? "done" : "todo",
                              })
                            }
                          />
                        </div>
                      </div>
                      {t.description && (
                        <p className="text-xs text-muted-foreground">
                          {t.description}
                        </p>
                      )}
                      <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                        {t.assignee_id && (
                          <span>Assigned: {getMemberName(t.assignee_id)}</span>
                        )}
                        {t.estimated_hours != null && (
                          <span>Est: {t.estimated_hours}h</span>
                        )}
                        {t.due_date && (
                          <span>
                            Due: {new Date(t.due_date).toLocaleString()}
                          </span>
                        )}
                      </div>
                      <div className="flex gap-2 mt-1">
                        <Button
                          size="xs"
                          variant="outline"
                          onClick={() => handleStartTimer(t.id)}
                        >
                          Start
                        </Button>
                        <Button
                          size="xs"
                          variant="outline"
                          onClick={() => handleStopTimer(t.id)}
                        >
                          Stop
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {currentUserTasks.length > 0 && (
              <div className="space-y-1">
                <h3 className="text-sm font-medium">My Tasks</h3>
                <div className="flex flex-wrap gap-2 text-xs">
                  {currentUserTasks.map((t) => (
                    <Badge key={t.id} variant="outline">
                      {t.title}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {aiPlan && aiPlan.assignments?.length > 0 && (
              <div className="space-y-2 rounded-md border p-3 text-xs">
                <p className="font-medium">Latest AI assignment plan</p>
                <ul className="list-disc pl-4 space-y-1">
                  {aiPlan.assignments.map((a) => (
                    <li key={a.task_id}>
                      <span className="font-semibold">{a.task_title}</span> →{" "}
                        <span>{getMemberName(a.assignee_id)}</span>{" "}
                      <span className="text-muted-foreground">
                        (score {a.assignee_score.toFixed(1)}, eta {a.estimated_hours.toFixed(1)}h)
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activePanel === "files" && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between gap-2">
            <div>
              <CardTitle>Project Files</CardTitle>
              <CardDescription>Upload and browse project artifacts.</CardDescription>
            </div>
            <Button size="sm" variant="ghost" onClick={() => setActivePanel(null)}>
              Close
            </Button>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <div>
                <Label htmlFor="file-upload" className="text-xs text-muted-foreground">
                  Upload file
                </Label>
                <Input
                  id="file-upload"
                  type="file"
                  disabled={uploadingFile}
                  onChange={handleUploadFile}
                />
                {uploadingFile && (
                  <p className="text-xs text-muted-foreground mt-1">
                    Uploading...
                  </p>
                )}
              </div>
              <div>
                <Label htmlFor="code-analysis" className="text-xs text-muted-foreground">
                  Analyze code (single file or .zip archive)
                </Label>
                <Input
                  id="code-analysis"
                  type="file"
                  accept=".js,.jsx,.ts,.tsx,.py,.java,.cpp,.c,.go,.zip"
                  disabled={analyzingCode}
                  onChange={handleAnalyzeCode}
                />
                {analyzingCode && (
                  <p className="text-xs text-muted-foreground mt-1">
                    Analyzing code...
                  </p>
                )}
              </div>
              {codeAnalysisResult && (
                <div className="mt-2 p-3 rounded-md border bg-muted/50 text-xs">
                  <p className="font-semibold mb-1">Analysis Results:</p>
                  <p>Overall Score: {codeAnalysisResult.score?.toFixed(1)}/100</p>
                  {codeAnalysisResult.details?.summary && (
                    <p className="mt-1 text-muted-foreground">
                      {codeAnalysisResult.details.summary}
                    </p>
                  )}
                  {codeAnalysisResult.details?.code_quality && (
                    <div className="mt-2">
                      <p className="font-medium">Code Quality: {codeAnalysisResult.details.code_quality.score?.toFixed(1)}/100</p>
                      {codeAnalysisResult.details.code_quality.issues?.length > 0 && (
                        <ul className="list-disc pl-4 mt-1">
                          {codeAnalysisResult.details.code_quality.issues.slice(0, 3).map((issue, idx) => (
                            <li key={idx} className="text-muted-foreground">{issue}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
            <div className="space-y-1 max-h-80 overflow-y-auto text-sm">
              {files.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No files uploaded yet.
                </p>
              ) : (
                files.map((f) => (
                  <div
                    key={f.id}
                    className="flex items-center justify-between rounded-md border p-2"
                  >
                    <div>
                      <p className="font-medium text-xs">{f.filename}</p>
                      <p className="text-[10px] text-muted-foreground">
                        {f.file_type || "file"} •{" "}
                        {new Date(f.uploaded_at).toLocaleDateString()}
                      </p>
                    </div>
                    <Button
                      size="xs"
                      variant="outline"
                      onClick={() => {
                        window.open(
                          `/files/projects/${projectId}/files/${f.id}/download`,
                          "_blank"
                        );
                      }}
                    >
                      Download
                    </Button>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Compact analytics preview when no specific panel is open */}
      {!activePanel && (
        <div className="grid gap-4 lg:grid-cols-3">
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Project Files</CardTitle>
              <CardDescription>Upload and browse project artifacts.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label htmlFor="file-upload" className="text-xs text-muted-foreground">
                  Upload file
                </Label>
                <Input
                  id="file-upload"
                  type="file"
                  disabled={uploadingFile}
                  onChange={handleUploadFile}
                />
                {uploadingFile && (
                  <p className="mt-1 text-xs text-muted-foreground">
                    Uploading...
                  </p>
                )}
              </div>
              <div className="space-y-1 max-h-56 overflow-y-auto text-sm">
                {files.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    No files uploaded yet.
                  </p>
                ) : (
                  files.map((f) => (
                    <div
                      key={f.id}
                      className="flex items-center justify-between rounded-md border p-2"
                    >
                      <div>
                        <p className="text-xs font-medium">{f.filename}</p>
                        <p className="text-[10px] text-muted-foreground">
                          {f.file_type || "file"} •{" "}
                          {new Date(f.uploaded_at).toLocaleDateString()}
                        </p>
                      </div>
                      <Button
                        size="xs"
                        variant="outline"
                        onClick={() => {
                          window.open(
                            `/files/projects/${projectId}/files/${f.id}/download`,
                            "_blank"
                          );
                        }}
                      >
                        Download
                      </Button>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Analytics</CardTitle>
              <CardDescription>
                Progress, completion, and member contribution overview.
              </CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <p className="text-xs text-muted-foreground">Completion</p>
                <p className="text-2xl font-semibold">
                  {analytics?.percent_complete?.toFixed(0) ?? 0}%
                </p>
                <ProgressBar value={analytics?.percent_complete ?? 0} />
                <p className="mt-1 text-xs text-muted-foreground">
                  {analytics?.tasks_completed ?? 0} /{" "}
                  {analytics?.total_tasks ?? 0} tasks done
                </p>
                <p className="text-xs text-muted-foreground">
                  Overdue: {analytics?.overdue_tasks ?? 0}
                </p>
              </div>
              <div className="space-y-2">
                <p className="text-xs text-muted-foreground">Daily completions</p>
                <MiniBarChart data={timelineData} />
              </div>
              <div className="space-y-2">
                <p className="text-xs text-muted-foreground">Member hours</p>
                <MiniBarChart data={memberHoursData} />
                <p className="mt-1 text-xs text-muted-foreground">
                  Avg completion:{" "}
                  {analytics?.avg_completion_minutes?.toFixed(1) ?? 0} min
                </p>
                <p className="text-xs text-muted-foreground">
                  Code quality avg:{" "}
                  {analytics?.code_quality_average?.toFixed(1) ?? 0}/100
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}


