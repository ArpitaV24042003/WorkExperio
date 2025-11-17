import { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";

export default function AiAssistant() {
  const { projectId } = useParams();
  const { user } = useAuthStore();
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatLog]);

  const sendMessage = async (event) => {
    event.preventDefault();
    if (!message.trim() || loading) return;
    
    const userMessage = message.trim();
    setMessage("");
    setChatLog((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);
    
    try {
      const { data } = await apiClient
        .post("/ai/assistant-chat", {
          project_id: projectId,
          user_id: user?.id,
          message: userMessage,
        })
        .catch(handleApiError);
      
      setChatLog((prev) => [...prev, { role: "assistant", content: data.response || data.message || "I'm here to help!" }]);
    } catch (error) {
      console.error(error);
      setChatLog((prev) => [...prev, { role: "assistant", content: "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="flex h-[80vh] flex-col">
      <CardHeader>
        <CardTitle>AI Assistant</CardTitle>
        <CardDescription>Chat with AI about your project, get help, and receive suggestions.</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 space-y-4 overflow-y-auto">
        {chatLog.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <p className="text-lg font-semibold">How can I help you today?</p>
              <p className="text-sm text-muted-foreground mt-2">
                Ask me about your project, get coding help, or request suggestions.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {chatLog.map((entry, index) => (
              <div
                key={`${entry.role}-${index}`}
                className={`flex gap-3 ${
                  entry.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {entry.role === "assistant" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold">
                    AI
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-3 ${
                    entry.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap break-words">{entry.content}</p>
                </div>
                {entry.role === "user" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary text-sm font-semibold">
                    You
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex gap-3 justify-start">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold">
                  AI
                </div>
                <div className="bg-muted rounded-lg px-4 py-3">
                  <div className="flex gap-1">
                    <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </CardContent>
      <CardFooter>
        <form className="flex w-full gap-2" onSubmit={sendMessage}>
          <Input
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Type your message..."
            disabled={loading}
            className="flex-1"
          />
          <Button type="submit" disabled={loading || !message.trim()}>
            {loading ? "Sending..." : "Send"}
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}

