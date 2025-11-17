import { useEffect, useState } from "react";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";

export default function Profile() {
  const { user } = useAuthStore();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      if (!user?.id) return;
      try {
        const { data } = await apiClient.get(`/users/${user.id}/profile`).catch(handleApiError);
        setProfile(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [user?.id]);

  if (loading) {
    return <p className="text-sm text-muted-foreground">Loading profile...</p>;
  }

  if (!profile) {
    return <p className="text-sm text-destructive">Unable to load profile.</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold">{profile.name}</h1>
        <p className="text-muted-foreground">{profile.email}</p>
        <div className="mt-2 flex items-center gap-2">
          <p className="text-xs text-muted-foreground">Your User ID:</p>
          <code className="rounded bg-muted px-2 py-1 text-xs font-mono">{profile.id}</code>
          <button
            onClick={() => {
              navigator.clipboard.writeText(profile.id);
              alert("User ID copied to clipboard!");
            }}
            className="text-xs text-primary hover:underline"
          >
            Copy
          </button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Profile Status</CardTitle>
            <CardDescription>Resume-powered profile completion.</CardDescription>
          </CardHeader>
          <CardContent>
            <Badge variant={profile.profile_completed ? "success" : "warning"}>
              {profile.profile_completed ? "Completed" : "Needs setup"}
            </Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Total XP</CardTitle>
            <CardDescription>Earn XP through projects, feedback, and AI analysis.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold">{profile.xp_points}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Skills</CardTitle>
          <CardDescription>Skills imported from resume or manually added.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {profile.skills.length ? (
            profile.skills.map((skill) => (
              <Badge key={skill.id} variant="outline">
                {skill.name}
              </Badge>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">No skills listed yet.</p>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Education</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {profile.educations.length ? (
              profile.educations.map((education) => (
                <div key={education.id}>
                  <p className="font-medium">{education.institution}</p>
                  <p className="text-sm text-muted-foreground">
                    {education.degree} {education.field}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">No education records yet.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Experience</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {profile.experiences.length ? (
              profile.experiences.map((experience) => (
                <div key={experience.id}>
                  <p className="font-medium">{experience.role}</p>
                  <p className="text-sm text-muted-foreground">
                    {experience.company} • {experience.start_date} - {experience.end_date || "Present"}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">No experience records yet.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

