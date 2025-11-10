// ProfilePage.jsx (replace entire file with this)
import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import "./LoginSignup.css";
import { apiRequest } from "../api";
import { aiParseResume } from "../ai";
import { useNavigate, useLocation } from "react-router-dom";

export default function ProfilePage() {
  const navigate = useNavigate();
  const location = useLocation();
  const search = new URLSearchParams(location.search);
  const firstTime = !!search.get("firstTime"); // true if onboarding

  const [loading, setLoading] = useState(false);
  const [resumeFile, setResumeFile] = useState(null);
  const [parsedResume, setParsedResume] = useState(null);
  const [apiError, setApiError] = useState(null);
  const [saving, setSaving] = useState(false);

  const [profile, setProfile] = useState({
    name: "",
    email: "",
    phone: "",
    linkedIn: "",
  });

  const [editMode, setEditMode] = useState({
    skills: false,
    education: false,
    projects: false,
    certificates: false,
    entities: false,
  });

  useEffect(() => {
    let ignore = false;
    (async () => {
      setLoading(true);
      setApiError(null);
      try {
        const me = await apiRequest("/users/me", "GET");
        if (!ignore && me) {
          setProfile({
            name: me.name || "",
            email: me.email || "",
            phone: me.phone || "",
            linkedIn: me.linkedIn || me.linkedin || "",
          });
          if (me.resumeParsed) setParsedResume(me.resumeParsed);
        }
      } catch (err) {
        if (!ignore) setApiError(err?.message || "Failed to load profile");
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    return () => (ignore = true);
  }, []);

  const handleResumeChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setResumeFile(file);
    setLoading(true);
    setApiError(null);
    try {
      // aiParseResume should accept a File/Blob and return structured JSON { skills:[], sections:{}, entities:{} }
      const data = await aiParseResume(file);
      setParsedResume(data);
    } catch (err) {
      setApiError(
        "Resume parsing failed: " + (err?.message || "Unknown error")
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setApiError(null);
    try {
      const payload = {
        ...profile,
        resumeFilename: resumeFile?.name,
        resumeParsed: {
          skills: parsedResume?.skills || [],
          sections: parsedResume?.sections || {},
          entities: parsedResume?.entities || {},
        },
        profileComplete: true,
      };
      const updated = await apiRequest("/users/me", "PATCH", payload);
      // update localStorage user copy (if any)
      try {
        const stored = JSON.parse(localStorage.getItem("user") || "{}");
        const merged = { ...(stored || {}), ...updated };
        localStorage.setItem("user", JSON.stringify(merged));
      } catch (e) {
        /* ignore */
      }

      alert("Profile saved!");
      if (firstTime) {
        // Continue onboarding -> open New Project flow
        navigate("/projects/new-flow");
      }
    } catch (err) {
      setApiError(err?.message || "Failed to save profile");
    } finally {
      setSaving(false);
    }
  };

  const renderSection = (title, key, data) => (
    <div key={key} style={{ marginBottom: "15px" }}>
      <h4 style={{ color: "#00e4ff", marginBottom: "4px" }}>{title}</h4>
      {!editMode[key] ? (
        <div>
          {Array.isArray(data) ? (
            data?.length ? (
              data.map((d, i) => <p key={i}>• {d}</p>)
            ) : (
              <p className="text-gray-400">None</p>
            )
          ) : (
            <pre
              style={{
                background: "#061b38",
                padding: "6px",
                fontSize: "12px",
              }}
            >
              {JSON.stringify(data || {}, null, 2)}
            </pre>
          )}
          <span
            className="nav-link"
            onClick={() => setEditMode({ ...editMode, [key]: true })}
          >
            Edit
          </span>
        </div>
      ) : (
        <textarea
          className="inputField"
          rows={4}
          defaultValue={
            Array.isArray(data)
              ? data.join("\n")
              : JSON.stringify(data, null, 2)
          }
          onBlur={(e) => {
            const val = e.target.value;
            setParsedResume((r) => ({
              ...(r || {}),
              [key]: Array.isArray(data)
                ? val.split("\n")
                : JSON.parse(val || "{}"),
            }));
            setEditMode({ ...editMode, [key]: false });
          }}
        />
      )}
    </div>
  );

  return (
    <div className="web-wrapper">
      <nav className="topbar">
        <h2 className="logoHeading">
          <span className="circleLogo">w</span> <i>WorkExperio</i>
        </h2>
      </nav>

      <div className="login-section">
        <div
          className="login-card"
          style={{ maxWidth: "650px", width: "100%" }}
        >
          <h2 style={{ marginBottom: "20px" }}>PROFILE</h2>

          {apiError && (
            <div className="mb-3 p-2 rounded bg-yellow-100 text-yellow-800">
              {apiError}
            </div>
          )}

          <div style={{ textAlign: "left" }}>
            <label style={{ color: "#00e4ff" }}>Name:</label>
            <input
              className="inputField"
              placeholder="Enter Name"
              value={profile.name}
              onChange={(e) => setProfile({ ...profile, name: e.target.value })}
            />
          </div>
          <div style={{ textAlign: "left" }}>
            <label style={{ color: "#00e4ff" }}>Email:</label>
            <input
              className="inputField"
              placeholder="Enter Email"
              value={profile.email}
              onChange={(e) =>
                setProfile({ ...profile, email: e.target.value })
              }
            />
          </div>
          <div style={{ textAlign: "left" }}>
            <label style={{ color: "#00e4ff" }}>Phone:</label>
            <input
              className="inputField"
              placeholder="Enter Phone"
              value={profile.phone}
              onChange={(e) =>
                setProfile({ ...profile, phone: e.target.value })
              }
            />
          </div>
          <div style={{ textAlign: "left" }}>
            <label style={{ color: "#00e4ff" }}>LinkedIn URL:</label>
            <input
              className="inputField"
              placeholder="LinkedIn Profile"
              value={profile.linkedIn}
              onChange={(e) =>
                setProfile({ ...profile, linkedIn: e.target.value })
              }
            />
          </div>

          <div style={{ textAlign: "left" }}>
            <label style={{ color: "#00e4ff" }}>Resume Upload:</label>
            <input
              type="file"
              onChange={handleResumeChange}
              className="inputField"
            />
          </div>

          {loading ? (
            <div style={{ textAlign: "left", padding: "15px" }}>
              <Loader2 className="animate-spin h-8 w-8" />
            </div>
          ) : (
            parsedResume && (
              <div
                style={{
                  maxHeight: "300px",
                  overflowY: "auto",
                  marginTop: "18px",
                  textAlign: "left",
                }}
              >
                {renderSection("Skills", "skills", parsedResume.skills || [])}
                {renderSection(
                  "Education",
                  "education",
                  parsedResume.sections?.Education || []
                )}
                {renderSection(
                  "Projects",
                  "projects",
                  parsedResume.sections?.Projects || []
                )}
                {renderSection(
                  "Certificates",
                  "certificates",
                  parsedResume.sections?.Certificates || []
                )}
                {renderSection(
                  "Entities",
                  "entities",
                  parsedResume.entities || {}
                )}
              </div>
            )
          )}

          <button
            className="login-btn mt-3"
            onClick={handleSave}
            disabled={saving}
            style={{ width: "100%" }}
          >
            {saving
              ? "Saving..."
              : firstTime
              ? "Save & Continue"
              : "SAVE PROFILE"}
          </button>
        </div>
      </div>
    </div>
  );
}
