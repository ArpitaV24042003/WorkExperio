import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip as ReTooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
  ResponsiveContainer,
} from "recharts";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";

const COLORS = ["#4f46e5", "#22c55e", "#eab308", "#ec4899", "#06b6d4", "#f97316"];

export default function PerformanceReport() {
  const { projectId } = useParams();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState(false);

  const loadAnalytics = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await apiClient
        .get(`/projects/${projectId}/analytics/overview`)
        .catch(handleApiError);
      setAnalytics(data || null);
    } catch (err) {
      setError(err.message || "Failed to load analytics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) {
      loadAnalytics();
    }
  }, [projectId]);

  const contributionPieData =
    analytics?.members?.map((m) => ({
      name: m.user_id.slice(0, 6),
      value: m.contribution_score,
    })) || [];

  const codeQualityBarData =
    analytics?.members?.map((m) => ({
      name: m.user_id.slice(0, 6),
      code_quality: m.code_quality_score,
    })) || [];

  const timelineLineData =
    analytics?.timeline?.map((t) => ({
      date: t.date.slice(5),
      completed: t.completed_count,
    })) || [];

  const timelinessStackedData =
    analytics?.members?.map((m) => ({
      name: m.user_id.slice(0, 6),
      on_time: m.task_consistency_score,
      late: 100 - m.task_consistency_score,
    })) || [];

  const layoutClass = expanded
    ? "fixed inset-0 z-40 bg-background p-4 md:p-8 overflow-y-auto"
    : "space-y-6";

  return (
    <div className={layoutClass}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-3xl font-semibold">Performance overview</h1>
          <p className="text-muted-foreground">
            Per-member and team metrics for this project (tasks, code quality, and participation).
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={loadAnalytics} disabled={loading}>
            {loading ? "Refreshing..." : "Refresh"}
          </Button>
          <Button variant="ghost" size="sm" onClick={() => setExpanded((prev) => !prev)}>
            ↗ {expanded ? "Close Full View" : "Expand Full View"}
          </Button>
        </div>
      </div>

      {error && <p className="mb-4 text-sm text-destructive">{error}</p>}

      {!analytics ? (
        <Card>
          <CardContent className="p-6 text-sm text-muted-foreground">
            {loading ? "Loading analytics..." : "No analytics available yet."}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* KPI cards */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader>
                <CardTitle>Completion</CardTitle>
                <CardDescription>Tasks completed in this project.</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-semibold">
                  {analytics.percent_complete.toFixed(0)}%
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {analytics.tasks_completed} / {analytics.total_tasks} tasks
                </p>
                <p className="text-xs text-muted-foreground">
                  Overdue: {analytics.overdue_tasks}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Team score</CardTitle>
                <CardDescription>Composite performance (0–100).</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-semibold">
                  {analytics.team_performance_score.toFixed(1)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  On-time: {(analytics.on_time_rate * 100).toFixed(1)}% • Delay:{" "}
                  {(analytics.delay_rate * 100).toFixed(1)}%
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Code quality</CardTitle>
                <CardDescription>Average score across contributions.</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-semibold">
                  {analytics.code_quality_average.toFixed(1)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">out of 100</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Participation</CardTitle>
                <CardDescription>Messages, uploads, and AI usage.</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-semibold">
                  {analytics.team_participation_score.toFixed(1)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {analytics.total_messages} messages • {analytics.total_files_uploaded} files •{" "}
                  {analytics.total_ai_interactions} AI calls
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Charts row 1: Contribution + Code quality */}
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Contribution breakdown</CardTitle>
                <CardDescription>
                  Weighted combination of tasks, files, and communication per member.
                </CardDescription>
              </CardHeader>
              <CardContent className="h-72">
                {contributionPieData.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No member contributions yet.</p>
                ) : (
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie
                        dataKey="value"
                        data={contributionPieData}
                        cx="50%"
                        cy="50%"
                        outerRadius={90}
                        label
                      >
                        {contributionPieData.map((entry, index) => (
                          <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <ReTooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Code quality per member</CardTitle>
                <CardDescription>Static analysis / heuristic scores 0–100.</CardDescription>
              </CardHeader>
              <CardContent className="h-72">
                {codeQualityBarData.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No code quality data yet.</p>
                ) : (
                  <ResponsiveContainer>
                    <BarChart data={codeQualityBarData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis domain={[0, 100]} />
                      <ReTooltip />
                      <Bar dataKey="code_quality" fill="#4f46e5" />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Charts row 2: Activity timeline + Timeliness */}
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Activity over time</CardTitle>
                <CardDescription>Tasks completed per day.</CardDescription>
              </CardHeader>
              <CardContent className="h-72">
                {timelineLineData.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No completed tasks yet.</p>
                ) : (
                  <ResponsiveContainer>
                    <LineChart data={timelineLineData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis allowDecimals={false} />
                      <ReTooltip />
                      <Line type="monotone" dataKey="completed" stroke="#22c55e" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>On-time vs late</CardTitle>
                <CardDescription>Per-member task consistency (approximate).</CardDescription>
              </CardHeader>
              <CardContent className="h-72">
                {timelinessStackedData.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No due-date tasks yet.</p>
                ) : (
                  <ResponsiveContainer>
                    <BarChart data={timelinessStackedData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis domain={[0, 100]} />
                      <ReTooltip />
                      <Legend />
                      <Bar dataKey="on_time" stackId="a" fill="#22c55e" name="On time %" />
                      <Bar dataKey="late" stackId="a" fill="#f97316" name="Late %" />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Simple per-member cards */}
          <Card>
            <CardHeader>
              <CardTitle>Member details</CardTitle>
              <CardDescription>Raw stats per member for inspection.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {analytics.members.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No member analytics yet. Ensure tasks, files, and messages are recorded.
                </p>
              ) : (
                analytics.members.map((m) => (
                  <div
                    key={m.user_id}
                    className="flex items-center justify-between rounded-md border p-3"
                  >
                    <div>
                      <p className="text-sm font-medium">Member {m.user_id.slice(0, 8)}...</p>
                      <p className="text-xs text-muted-foreground">
                        {m.tasks_completed} tasks • {m.total_hours.toFixed(1)}h •{" "}
                        {m.files_uploaded} files • {m.messages_sent} messages
                      </p>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <Badge variant="outline">
                        Contribution {m.contribution_score.toFixed(1)}
                      </Badge>
                      <Badge variant="secondary">
                        Consistency {m.task_consistency_score.toFixed(1)}%
                      </Badge>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

