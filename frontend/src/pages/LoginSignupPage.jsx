import { useState } from "react";
import { Link } from "react-router-dom";
import "./LoginSignup.css";
import { apiRequest } from "../api";

export default function LoginSignupPage() {
  const [isSignup, setIsSignup] = useState(false);

  // const handleGitHubAuth = () => {
  //   // redirect to your backend’s GitHub authentication route:
  //   window.location.href = "/api/auth/github";
  // };
  const handleGitHubAuth = () => {
    window.location.href = `${import.meta.env.VITE_API_URL}/auth/github/login`;
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
          {!isSignup ? (
            <>
              <h3 className="login-title">Log In</h3>
              <button className="login-btn" onClick={handleGitHubAuth}>
                Continue with GitHub
              </button>
              <p className="signup-info">
                New here?{" "}
                <span className="signup-link" onClick={() => setIsSignup(true)}>
                  Create account
                </span>
              </p>
            </>
          ) : (
            <>
              <h3 className="login-title">Sign Up</h3>
              <button className="signup-btn" onClick={handleGitHubAuth}>
                Continue with GitHub
              </button>
              <p className="signup-info">
                Already have an account?{" "}
                <span
                  className="signup-link"
                  onClick={() => setIsSignup(false)}
                >
                  Log In
                </span>
              </p>
            </>
          )}
        </div>
      </section>
    </div>
  );
}
