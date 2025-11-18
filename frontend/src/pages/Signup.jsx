import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiClient, handleApiError } from "../lib/api";
import { useAuthStore } from "../store/auth";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { PasswordInput } from "../components/ui/password-input";
import { Label } from "../components/ui/label";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../components/ui/card";

export default function Signup() {
  const navigate = useNavigate();
  const { setCredentials } = useAuthStore();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await apiClient.post("/auth/signup", form, { timeout: 15000 }).catch(handleApiError);
      const token = data.access_token;
      setCredentials({ token, user: { name: form.name, email: form.email } });
      
      // Fetch user profile with timeout
      try {
        const me = await apiClient.get("/users/me", { timeout: 10000 }).catch(handleApiError);
        setCredentials({ token, user: me.data });
      } catch (profileError) {
        // If profile fetch fails, still allow signup with basic info
        console.warn("Failed to fetch user profile:", profileError);
      }
      
      navigate("/profile-setup");
    } catch (err) {
      // Better error handling for network issues
      let errorMessage = "Signup failed. Please try again.";
      
      if (err.message) {
        errorMessage = err.message;
      } else if (err?.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err?.response?.status === 400 || err?.response?.status === 422) {
        errorMessage = "Invalid input. Please check your information and try again.";
      } else if (err?.response?.status === 409) {
        errorMessage = "An account with this email already exists. Please sign in instead.";
      } else if (err?.response?.status >= 500) {
        errorMessage = "Server error. Please try again in a moment.";
      } else if (!err?.response) {
        errorMessage = "Cannot connect to server. Please check your connection.";
      }
      
      setError(errorMessage);
      console.error("Signup error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary/10 via-background to-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Create your account</CardTitle>
          <CardDescription>Join WorkExperio to match skills, teams, and projects intelligently.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input id="name" name="name" value={form.name} onChange={handleChange} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" name="email" type="email" value={form.email} onChange={handleChange} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <PasswordInput id="password" name="password" value={form.password} onChange={handleChange} required />
            </div>
            {error ? <p className="text-sm text-destructive">{error}</p> : null}
            <Button className="w-full" type="submit" disabled={loading}>
              {loading ? "Creating account..." : "Sign Up"}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex justify-between">
          <p className="text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link className="text-primary underline" to="/login">
              Sign in
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}

