// src/pages/LoginSignupPage.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./LoginSignup.css";
import { apiRequest, fetchCurrentUser, setToken } from "../api";
import { Eye, EyeOff } from "lucide-react";

export default function LoginSignupPage() {
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const navigate = useNavigate();

  // fallback backend URL (used for manual fetch fallback only)
  const backendUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
  void backendUrl;

  /**
   * Normalize and persist a "safe" user snapshot to localStorage.
   * Accepts the canonical user object returned from GET /users/me or a login payload.
   */
  function persistSafeUser(userObj, token = null) {
    const safeUser = {
      id: userObj?.id || userObj?._id || null,
      name: userObj?.name || userObj?.fullName || null,
      email: userObj?.email || null,
      // prefer parsed resume summary field names used by backend
      resumeParsed:
        userObj?.resumeParsed ??
        userObj?.parsed_resume_summary ??
        userObj?.parsedResume ??
        null,
      // Only treat as needs-onboarding when explicitly false
      profileComplete:
        userObj?.profile_complete === false
          ? false
          : userObj?.profileComplete === false
          ? false
          : userObj?.profile_complete === true ||
            userObj?.profileComplete === true
          ? true
          : null,
      createdAt: userObj?.createdAt ?? userObj?.created_at ?? null,
      raw: userObj,
    };

    try {
      if (token) setToken(token);
      localStorage.setItem("user", JSON.stringify(safeUser));
      localStorage.setItem("lastLogin", new Date().toISOString());
    } catch (e) {
      // ignore storage errors
      // But still set token separately if available
      if (token) setToken(token);
    }
    return safeUser;
  }

  // Manual fallback to GET /users/me if fetchCurrentUser fails (rare)
  async function fetchCanonicalUserFallback(token) {
    if (!token) return null;
    try {
      const res = await fetch(`${backendUrl}/users/me`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setLoading(true);

    try {
      if (isSignup) {
        // Register user -> prompt them to log in
        await apiRequest("/users/register", "POST", { name, email, password });
        alert("Signup successful! Please log in.");
        setIsSignup(false);
        setPassword("");
        setName("");
        setEmail("");
        setLoading(false);
        return;
      }

      // LOGIN
      const data = await apiRequest("/users/login", "POST", {
        email,
        password,
      });

      // Accept several possible shapes:
      // - { token: "...", user: { ... } }
      // - { token: "..." }
      // - { user: {...} }
      // - legacy: user object directly
      const token =
        data?.token ||
        data?.accessToken ||
        data?.access_token ||
        data?.user?.token ||
        data?.user?.accessToken ||
        null;

      const loginUserObj = data?.user || (data?.id ? data : null);

      // If token present, persist via setToken immediately so fetchCurrentUser works
      if (token) {
        setToken(token);
      }

      // Now fetch the canonical user information from the backend if possible.
      // Preferred: fetchCurrentUser() (uses apiRequest + token)
      let canonical = null;
      try {
        canonical = await fetchCurrentUser();
      } catch (err) {
        // fallback: try manual fetch using token
        if (token) {
          canonical = await fetchCanonicalUserFallback(token);
        }
      }

      // If canonical not available, fall back to login-user object or raw response
      if (!canonical) canonical = loginUserObj || data || null;

      // Persist normalized snapshot and token
      const safeUser = persistSafeUser(canonical || {}, token);

      // Decide onboarding vs main dashboard:
      // Only treat as "needs onboarding" when profileComplete is explicitly false
      const needsProfile = safeUser.profileComplete === false;

      if (needsProfile) {
        navigate("/profile?firstTime=1");
      } else {
        navigate("/dashboard");
      }
    } catch (err) {
      // normalize message
      const message =
        err?.message ||
        (err?.data &&
          (err.data.message || err.data.error || err.data.detail)) ||
        "Something went wrong";
      setErrorMsg(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="web-wrapper">
      <nav className="topbar">
        <h2 className="logoHeading">
          <span className="circleLogo">w</span> <i>WorkExperio</i>
        </h2>
        <Link to="/" className="nav-link">
          Home
        </Link>
        {/* Add profile link to your global nav (App.jsx) so returning users can edit profile anytime */}
      </nav>

      <section className="login-section">
        <div className="login-card">
          <h3 className="login-title">{isSignup ? "Sign Up" : "Log In"}</h3>

          {errorMsg && (
            <div
              style={{
                color: "#ffbaba",
                background: "#3a1b1b",
                padding: 10,
                borderRadius: 6,
                marginBottom: 12,
              }}
            >
              {errorMsg}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {isSignup && (
              <input
                className="inputField"
                type="text"
                placeholder="Full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                autoComplete="name"
                disabled={loading}
              />
            )}

            <input
              className="inputField"
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              disabled={loading}
            />

            <div className="password-wrapper">
              <input
                className="inputField"
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete={isSignup ? "new-password" : "current-password"}
                disabled={loading}
              />
              <button
                type="button"
                className="eye-icon"
                aria-label={showPassword ? "Hide password" : "Show password"}
                onClick={() => setShowPassword((s) => !s)}
                title={showPassword ? "Hide password" : "Show password"}
                disabled={loading}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>

            <button type="submit" className="login-btn" disabled={loading}>
              {loading
                ? isSignup
                  ? "Signing up..."
                  : "Logging in..."
                : isSignup
                ? "Sign Up"
                : "Log In"}
            </button>
          </form>

          <p className="signup-info">
            {isSignup ? "Already have an account?" : "New here?"}{" "}
            <span
              className="signup-link"
              onClick={() => {
                if (loading) return;
                setIsSignup(!isSignup);
                setErrorMsg("");
              }}
              style={{ cursor: "pointer" }}
            >
              {isSignup ? "Log In" : "Create account"}
            </span>
          </p>
        </div>
      </section>
    </div>
  );
}
