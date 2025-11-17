import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../components/ui/card";
import { Button } from "../components/ui/button";

export default function UploadResume() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setStatus("Please select a PDF resume to upload.");
      return;
    }
    setLoading(true);
    setStatus("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      await apiClient.post("/resumes/parse", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatus("Resume uploaded and parsed successfully.");
      setFile(null);
      // Navigate to profile setup after successful upload
      setTimeout(() => {
        navigate("/profile-setup");
      }, 1500);
    } catch (error) {
      handleApiError(error);
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="max-w-xl">
      <CardHeader>
        <CardTitle>Upload Resume</CardTitle>
        <CardDescription>Support for PDF resumes. The parser will auto-fill your profile data.</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <input
            accept="application/pdf"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            type="file"
            className="w-full rounded-md border border-dashed p-4"
          />
          <Button type="submit" disabled={loading}>
            {loading ? "Uploading..." : "Upload"}
          </Button>
        </form>
      </CardContent>
      <CardFooter>{status ? <p className="text-sm text-muted-foreground">{status}</p> : null}</CardFooter>
    </Card>
  );
}

