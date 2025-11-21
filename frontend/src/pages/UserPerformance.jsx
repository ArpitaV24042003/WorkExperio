import { useEffect, useState } from "react";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";

function Sparkline({ points }) {
  if (!points || points.length === 0) {
    return <p className="text-[10px] text-muted-foreground">No activity yet.</p>;
  }
  const max = Math.max(...points, 1);
  return (
    <div className="flex items-end gap-0.5 h-8">
      {points.map((v, idx) => (
        <div
          // eslint-disable-next-line react/no-array-index-key
          key={idx}
          className="flex-1 bg-primary/60"
          style={{ height: `${(v / max) * 100}%` }}
        />
      ))}
    </div>
  );
}

export default function UserPerformance() {
  const { user } = useAuthStore();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const downloadCsv = () => {
    if (!data || !data.projects) return;
    const header = ["project_id", "tasks_completed", "total_hours", "code_quality_score"];
    const rows = data.projects.map((p) => [
      p.project_id,
      p.tasks_completed,
      p.total_hours,
      p.code_quality_score,
    ]);
    const csv = [header.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "workexperio-performance.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    const load = async () => {
      if (!user?.id) return;
      setLoading(true);
      setError("");
      try {
        const { data: analytics } = await apiClient
          .get(`/users/${user.id}/analytics`)
          .catch(handleApiError);
        setData(analytics || null);
      } catch (err) {
        console.error("User analytics error:", err);
        setError(err.message || "Failed to load performance analytics.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [user?.id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[300px]">
        <p className="text-sm text-muted-foreground">Loading performance...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[300px] space-y-2">
        <p className="text-sm text-destructive">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-[300px]">
        <p className="text-sm text-muted-foreground">No analytics available yet.</p>
      </div>
    );
  }

  const globalKpis = {
    avgCompletion: data.avg_completion_minutes ?? 0,
    onTimeRatio: (data.on_time_completion_ratio ?? 0) * 100,
    codeQuality: data.code_quality_average ?? 0,
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold">Your Performance</h1>
        <p className="text-muted-foreground">
          Project-by-project contributions, hours, and quality trends.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Avg completion time</CardTitle>
            <CardDescription>Across all tasks with tracked time.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold">
              {globalKpis.avgCompletion.toFixed(1)}
            </p>
            <p className="text-xs text-muted-foreground mt-1">minutes per task</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>On-time completion</CardTitle>
            <CardDescription>Tasks finished on or before due date.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold">
              {globalKpis.onTimeRatio.toFixed(0)}%
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Code quality</CardTitle>
            <CardDescription>Average score from code analysis hooks.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold">
              {globalKpis.codeQuality.toFixed(1)}
            </p>
            <p className="text-xs text-muted-foreground mt-1">out of 100</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between gap-2">
            <div>
              <CardTitle>Per-project contributions</CardTitle>
              <CardDescription>
                Tasks completed, hours logged, and quality per project.
              </CardDescription>
            </div>
            {data.projects.length > 0 && (
              <button
                type="button"
                onClick={downloadCsv}
                className="text-xs font-medium text-primary underline-offset-2 hover:underline"
              >
                Download CSV
              </button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {data.projects.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No contributions recorded yet. Start a project and track your time.
            </p>
          ) : (
            data.projects.map((p) => (
              <div
                key={`${p.project_id}-${p.user_id}`}
                className="rounded-md border p-3 space-y-1"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">
                    Project {p.project_id?.slice(0, 8)}...
                  </span>
                  <Badge variant="outline">
                    {p.tasks_completed} tasks • {p.total_hours.toFixed(1)}h
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  Code quality: {p.code_quality_score.toFixed(1)}/100
                </p>
                <Sparkline
                  points={Array.from(
                    { length: Math.min(10, Math.max(1, p.tasks_completed)) },
                    () => 1
                  )}
                />
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}


