import { useState } from "react";
import { Loader2 } from "lucide-react";
import "./LoginSignup.css";

export default function ProfilePage() {
  const [loading, setLoading] = useState(false);
  const [resumeFile, setResumeFile] = useState(null);
  const [parsedResume, setParsedResume] = useState(null);

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

  const handleResumeChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setResumeFile(file);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("resume", file);
      const res = await fetch("/api/resumes/parse", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setParsedResume(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = () => {
    const payload = {
      ...profile,
      resume: resumeFile?.name,
      skills: parsedResume?.skills,
      education: parsedResume?.sections?.Education,
      projects: parsedResume?.sections?.Projects,
      certificates: parsedResume?.sections?.Certificates,
      entities: parsedResume?.entities,
    };
    console.log(payload);
    alert("Saved!");
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
            Array.isArray(data) ? data.join("\n") : JSON.stringify(data, null, 2)
          }
          onBlur={(e) => {
            const val = e.target.value;
            setParsedResume((r) => ({
              ...r,
              [key]: Array.isArray(data) ? val.split("\n") : JSON.parse(val),
            }));
            setEditMode({ ...editMode, [key]: false });
          }}
        />
      )}
    </div>
  );

  return (
    <div className="web-wrapper">
      {/* TOP HEADER BAR  */}
      <nav className="topbar">
        <h2 className="logoHeading">
          <span className="circleLogo">w</span> <i>WorkExperio</i>
        </h2>
      </nav>

      <div className="login-section">
        <div className="login-card" style={{ maxWidth: "550px", width: "100%" }}>
          <h2 style={{ marginBottom: "25px" }}> PROFILE</h2>

          {/* editable boxes */}
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
              onChange={(e) => setProfile({ ...profile, email: e.target.value })}
            />
          </div>
          <div style={{ textAlign: "left" }}>
            <label style={{ color: "#00e4ff" }}>Phone:</label>
            <input
              className="inputField"
              placeholder="Enter Phone"
              value={profile.phone}
              onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
            />
          </div>
          <div style={{ textAlign: "left" }}>
            <label style={{ color: "#00e4ff" }}>LinkedIn URL:</label>
            <input
              className="inputField"
              placeholder="LinkedIn Profile"
              value={profile.linkedIn}
              onChange={(e) => setProfile({ ...profile, linkedIn: e.target.value })}
            />
          </div>

          <div style={{ textAlign: "left" }}>
            <label style={{ color: "#00e4ff" }}>Resume Upload:</label>
            <input type="file" onChange={handleResumeChange} className="inputField" />
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

          <button className="login-btn mt-3" onClick={handleSave}>
            SAVE PROFILE
          </button>
        </div>
      </div>
    </div>
  );
}


