import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./LoginSignup.css";
import { apiRequest } from "../api";
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

  // If your apiRequest already sets the base URL, you can remove this.
  const backendUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
  void backendUrl; // avoid unused var if not used directly

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setLoading(true);

    try {
      if (isSignup) {
        // Register user
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
      const data = await apiRequest("/users/login", "POST", { email, password });

      // Accept several possible shapes:
      // 1) { token: "...", user: { ... } }
      // 2) { user: { ... } }
      // 3) { id, name, email, ... } (user directly)
      const token = data?.token || data?.accessToken || null;
      const userObj = data?.user || (data?.id ? data : data);

      // Save token if provided
      if (token) localStorage.setItem("token", token);

      // Save user info (strip sensitive fields if present)
      const safeUser = {
        id: userObj?.id || userObj?._id || null,
        name: userObj?.name || userObj?.fullName || null,
        email: userObj?.email || null,
        resumeParsed: userObj?.resumeParsed ?? null,
        profileComplete: userObj?.profileComplete ?? null,
        createdAt: userObj?.createdAt ?? null,
        // keep the raw object too for flexibility
        raw: userObj,
      };

      localStorage.setItem("user", JSON.stringify(safeUser));
      localStorage.setItem("lastLogin", new Date().toISOString());

      // Decide onboarding vs main dashboard
      // If profileComplete === false OR resumeParsed is missing/null -> treat as needs onboarding
      const needsProfile =
        safeUser.profileComplete === false ||
        safeUser.profileComplete === null ||
        !safeUser.resumeParsed;

      if (needsProfile) {
        // firstTime flag so ProfilePage knows to continue to project flow after save
        navigate("/profile?firstTime=1");
      } else {
        navigate("/dashboard");
      }
    } catch (err) {
      // normalize message
      const message =
        err?.message ||
        (err?.error && typeof err.error === "string" ? err.error : null) ||
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
      </nav>

      <section className="login-section">
        <div className="login-card">
          <h3 className="login-title">{isSignup ? "Sign Up" : "Log In"}</h3>

          {errorMsg && (
            <div style={{ color: "#ffbaba", background: "#3a1b1b", padding: 10, borderRadius: 6, marginBottom: 12 }}>
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
              {loading ? (isSignup ? "Signing up..." : "Logging in...") : isSignup ? "Sign Up" : "Log In"}
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
