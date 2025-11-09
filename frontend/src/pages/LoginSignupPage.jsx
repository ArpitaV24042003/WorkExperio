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
  const navigate = useNavigate();

  // If your apiRequest already sets the base URL, you can remove this.
  const backendUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
  void backendUrl; // avoid unused var if not used directly

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isSignup) {
        await apiRequest("/users/register", "POST", { name, email, password });
        alert("Signup successful! Please log in.");
        setIsSignup(false);
        setPassword("");
      } else {
        const data = await apiRequest("/users/login", "POST", {
          email,
          password,
        });
        localStorage.setItem("user", JSON.stringify(data));
        localStorage.setItem("lastLogin", new Date().toISOString());
        navigate("/dashboard");
      }
    } catch (err) {
      alert("Error: " + (err?.message || "Something went wrong"));
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
              />
              <button
                type="button"
                className="eye-icon"
                aria-label={showPassword ? "Hide password" : "Show password"}
                onClick={() => setShowPassword((s) => !s)}
                title={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>

            <button type="submit" className="login-btn">
              {isSignup ? "Sign Up" : "Log In"}
            </button>
          </form>

          <p className="signup-info">
            {isSignup ? "Already have an account?" : "New here?"}{" "}
            <span
              className="signup-link"
              onClick={() => setIsSignup(!isSignup)}
            >
              {isSignup ? "Log In" : "Create account"}
            </span>
          </p>
        </div>
      </section>
    </div>
  );
}
