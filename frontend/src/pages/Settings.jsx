import { useEffect, useState } from "react";
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
  const [theme, setTheme] = useState("system");

  useEffect(() => {
    try {
      const storedTheme = localStorage.getItem("theme") || "system";
      setTheme(storedTheme);
      applyTheme(storedTheme);
    } catch {
      // ignore
    }
  }, []);

  const applyTheme = (value) => {
    const root = document.documentElement;
    if (value === "dark") {
      root.classList.add("dark");
    } else if (value === "light") {
      root.classList.remove("dark");
    } else {
      // system: let OS decide, remove explicit override
      root.classList.remove("dark");
    }
  };

  const handleThemeChange = (value) => {
    setTheme(value);
    try {
      localStorage.setItem("theme", value);
    } catch {
      // ignore storage errors
    }
    applyTheme(value);
  };

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
    <div className="space-y-6 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Account settings</CardTitle>
          <CardDescription>Update your account information.</CardDescription>
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
        <CardFooter>
          {status ? <p className="text-sm text-muted-foreground">{status}</p> : null}
        </CardFooter>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Choose a theme for the app.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <Label htmlFor="theme">Theme</Label>
          <select
            id="theme"
            className="border rounded-md px-2 py-1 text-sm bg-background"
            value={theme}
            onChange={(e) => handleThemeChange(e.target.value)}
          >
            <option value="system">System default</option>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
          <p className="text-xs text-muted-foreground">
            Theme preference is stored locally in this browser.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

