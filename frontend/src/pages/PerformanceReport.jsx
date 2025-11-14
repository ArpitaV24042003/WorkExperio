import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";

export default function PerformanceReport() {
  const { projectId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runAnalysis = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await apiClient.post(`/ai/analyze-performance/${projectId}`).catch(handleApiError);
      setReport(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runAnalysis();
  }, [projectId]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold">Performance overview</h1>
          <p className="text-muted-foreground">AI evaluates participation, consistency, and communication.</p>
        </div>
        <Button onClick={runAnalysis} disabled={loading}>
          {loading ? "Analyzing..." : "Re-run analysis"}
        </Button>
      </div>

      {error ? <p className="text-sm text-destructive">{error}</p> : null}

      {report ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Participation</CardTitle>
              <CardDescription>How active members are in discussions.</CardDescription>
            </CardHeader>
            <CardContent>
              <Badge variant="secondary">{report.participation_score}</Badge>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Task consistency</CardTitle>
              <CardDescription>Reliability completing assigned work.</CardDescription>
            </CardHeader>
            <CardContent>
              <Badge variant="secondary">{report.task_consistency_score}</Badge>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Communication</CardTitle>
              <CardDescription>Quality and frequency of team updates.</CardDescription>
            </CardHeader>
            <CardContent>
              <Badge variant="secondary">{report.communication_score}</Badge>
            </CardContent>
          </Card>
        </div>
      ) : (
        <Card>
          <CardContent className="p-6 text-sm text-muted-foreground">Run analysis to see performance insights.</CardContent>
        </Card>
      )}
    </div>
  );
}

