// src/pages/LoginSignupPage.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./LoginSignup.css";
import { apiRequest } from "../api"; // if you don't have this, see the helper below

export default function LoginSignupPage() {
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("handleSubmit called", { isSignup, email, name });
    setLoading(true);

    try {
      if (isSignup) {
        const res = await apiRequest("/users/register", "POST", {
          name,
          email,
          password,
        });
        console.log("signup response", res);
        alert("Signup successful! Please log in.");
        setIsSignup(false);
        setName("");
        setPassword("");
        setEmail("");
      } else {
        const data = await apiRequest("/users/login", "POST", {
          email,
          password,
        });
        console.log("login response", data);
        // Save token or user as your app expects
        localStorage.setItem("user", JSON.stringify(data));
        // navigate to Project Dashboard page
        navigate("/dashboard");
      }
    } catch (err) {
      console.error("Auth error:", err);
      alert("Error: " + (err?.message || JSON.stringify(err)));
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
          <form onSubmit={handleSubmit}>
            {isSignup && (
              <input
                className="inputField"
                type="text"
                placeholder="Full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            )}
            <input
              className="inputField"
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              className="inputField"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

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
