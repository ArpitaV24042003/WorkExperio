import { useState } from "react";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";

export default function Settings() {
  const { user, setCredentials, token } = useAuthStore();
  const [name, setName] = useState(user?.name ?? "");
  const [status, setStatus] = useState("");

  const updateProfile = async (event) => {
    event.preventDefault();
    if (!user?.id) return;
    try {
      const { data } = await apiClient
        .patch(`/users/${user.id}/profile`, { name })
        .catch(handleApiError);
      setStatus("Profile updated.");
      setCredentials({ token, user: { ...user, name: data.name } });
    } catch (error) {
      setStatus(error.message);
    }
  };

  return (
    <Card className="max-w-xl">
      <CardHeader>
        <CardTitle>Account settings</CardTitle>
        <CardDescription>Update your account information and preferences.</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={updateProfile}>
          <div className="space-y-2">
            <Label htmlFor="name">Display name</Label>
            <Input id="name" value={name} onChange={(event) => setName(event.target.value)} />
          </div>
          <Button type="submit">Save changes</Button>
        </form>
      </CardContent>
      <CardFooter>{status ? <p className="text-sm text-muted-foreground">{status}</p> : null}</CardFooter>
    </Card>
  );
}

