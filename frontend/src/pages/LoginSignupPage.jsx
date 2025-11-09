// src/pages/LoginSignupPage.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./LoginSignup.css";
import { apiRequest } from "../api";

export default function LoginSignupPage() {
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const navigate = useNavigate();

  const backendUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isSignup) {
        await apiRequest("/users/register", "POST", { name, email, password });
        alert("Signup successful! Please log in.");
        setIsSignup(false);
      } else {
        const data = await apiRequest("/users/login", "POST", {
          email,
          password,
        });
        localStorage.setItem("user", JSON.stringify(data));
        navigate("/dashboard"); // or "/project-dashboard" if you prefer
      }
    } catch (err) {
      alert("Error: " + err.message);
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
                autoComplete="name"
                required
              />
            )}
            <input
              className="inputField"
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
            <input
              className="inputField"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={isSignup ? "new-password" : "current-password"}
              required
            />
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
