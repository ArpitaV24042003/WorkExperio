import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";

export default function ProfileSetup() {
  const navigate = useNavigate();
  const { user, setCredentials, token } = useAuthStore();
  const [profile, setProfile] = useState(null);
  const [selectedResume, setSelectedResume] = useState("");
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchProfile = async () => {
      if (!user?.id) return;
      try {
        const { data } = await apiClient.get(`/users/${user.id}/profile`).catch(handleApiError);
        setProfile(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [user?.id]);

  const applyResume = async () => {
    if (!selectedResume) {
      setError("Select a resume to import.");
      return;
    }
    setUpdating(true);
    try {
      const { data } = await apiClient
        .post(`/users/${user.id}/profile/from-resume/${selectedResume}`)
        .catch(handleApiError);
      setProfile(data);
      setCredentials({ token, user: { ...user, profile_completed: true } });
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return <p className="text-sm text-muted-foreground">Loading profile setup...</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold">Complete your profile</h1>
        <p className="text-muted-foreground">Import resume data or fill out your experience manually.</p>
      </div>

      {error ? <p className="text-sm text-destructive">{error}</p> : null}

      <Card>
        <CardHeader>
          <CardTitle>Resumes</CardTitle>
          <CardDescription>Select a resume to import into your profile.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {profile?.resumes?.length ? (
            <div className="space-y-3">
              {profile.resumes.map((resume) => (
                <label
                  key={resume.id}
                  className={`flex cursor-pointer items-center justify-between rounded-md border p-3 ${
                    selectedResume === resume.id ? "border-primary bg-primary/5" : ""
                  }`}
                >
                  <div>
                    <p className="font-medium">{resume.filename}</p>
                    <p className="text-xs text-muted-foreground">
                      Uploaded {new Date(resume.uploaded_at).toLocaleString()}
                    </p>
                  </div>
                  <input
                    checked={selectedResume === resume.id}
                    onChange={() => setSelectedResume(resume.id)}
                    type="radio"
                    className="h-4 w-4"
                    name="resume"
                  />
                </label>
              ))}
            </div>
          ) : (
            <div className="rounded-md border border-dashed p-6 text-center">
              <p className="text-sm text-muted-foreground">
                No resumes uploaded yet. Upload one to auto-fill your profile.
              </p>
              <Button className="mt-3" onClick={() => navigate("/upload-resume")}>
                Upload resume
              </Button>
            </div>
          )}
        </CardContent>
        <CardFooter className="justify-between">
          <Badge variant={profile?.profile_completed ? "success" : "warning"}>
            {profile?.profile_completed ? "Profile completed" : "Pending"}
          </Badge>
          <Button onClick={applyResume} disabled={!selectedResume || updating}>
            {updating ? "Applying..." : "Apply Resume"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}

