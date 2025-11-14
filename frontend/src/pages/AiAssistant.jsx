import { useState } from "react";
import { useParams } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";

export default function AiAssistant() {
  const { projectId } = useParams();
  const { user } = useAuthStore();
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (event) => {
    event.preventDefault();
    if (!message.trim()) return;
    setLoading(true);
    try {
      const { data } = await apiClient
        .post("/ai/assistant-chat", {
          project_id: projectId,
          user_id: user?.id,
          message,
        })
        .catch(handleApiError);
      setChatLog((prev) => [...prev, { role: "user", content: message }, { role: "assistant", content: data.response }]);
      setMessage("");
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>AI assistant</CardTitle>
          <CardDescription>Ask about next steps, summaries, or coding help.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <form className="flex gap-2" onSubmit={sendMessage}>
            <textarea
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="What should I do next?"
              rows={3}
            />
            <Button type="submit" disabled={loading}>
              {loading ? "Thinking..." : "Send"}
            </Button>
          </form>
          <div className="space-y-3">
            {chatLog.length === 0 ? (
              <p className="text-sm text-muted-foreground">No messages yet. Start a conversation.</p>
            ) : (
              chatLog.map((entry, index) => (
                <div
                  key={`${entry.role}-${index}`}
                  className={`rounded-md border p-3 text-sm ${
                    entry.role === "assistant" ? "bg-primary/5" : "bg-secondary/5"
                  }`}
                >
                  <p className="font-semibold capitalize">{entry.role}</p>
                  <p>{entry.content}</p>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

