import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";

export default function CreateProject() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [profile, setProfile] = useState(null);
  const [form, setForm] = useState({ title: "", description: "", ai_generated: false });
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

  const createProject = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const { data } = await apiClient.post("/projects", form).catch(handleApiError);
      navigate(`/projects/${data.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateAiIdea = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        skills: profile?.skills?.map((skill) => skill.name) ?? [],
        experience_level: profile?.experiences?.length ? "intermediate" : "beginner",
      };
      const { data } = await apiClient.post("/projects/ai-generate", payload).catch(handleApiError);
      setAiIdea(data);
      setForm({
        title: data.title,
        description: data.description,
        ai_generated: true,
        team_type: "none",
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-6 md:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Create project</CardTitle>
          <CardDescription>Define a project manually or use AI suggestions based on your skills.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={createProject}>
            <div className="space-y-2">
              <Label htmlFor="title">Title</Label>
              <Input id="title" name="title" value={form.title} onChange={handleChange} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <textarea
                id="description"
                name="description"
                value={form.description}
                onChange={handleChange}
                required
                className="min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
            {error ? <p className="text-sm text-destructive">{error}</p> : null}
            <Button type="submit" disabled={loading}>
              {loading ? "Creating..." : "Create project"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>AI Project Assistant</CardTitle>
          <CardDescription>Generate an idea using your skills, experience, and interest areas.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button variant="outline" onClick={generateAiIdea} disabled={loading}>
            {loading ? "Generating..." : "Generate idea"}
          </Button>
          {aiIdea ? (
            <div className="space-y-3 rounded-md border p-4">
              <p className="text-sm font-semibold">{aiIdea.title}</p>
              <p className="text-sm text-muted-foreground">{aiIdea.description}</p>
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground">Milestones</p>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
                  {aiIdea.milestones.map((milestone) => (
                    <li key={milestone}>{milestone}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : null}
        </CardContent>
        <CardFooter>
          <p className="text-xs text-muted-foreground">Use the generated idea to pre-fill the form above.</p>
        </CardFooter>
      </Card>
    </div>
  );
}

