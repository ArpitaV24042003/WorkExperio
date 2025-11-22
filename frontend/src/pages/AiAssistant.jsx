import { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import ReactMarkdown from "react-markdown";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";

export default function AiAssistant() {
  const { projectId } = useParams();
  const { user } = useAuthStore();
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatLog]);

  // Load project-scoped conversation history on mount
  useEffect(() => {
    const loadHistory = async () => {
      if (!user?.id || !projectId) {
        setLoadingHistory(false);
        return;
      }
      try {
        const { data } = await apiClient
          .get(`/projects/${projectId}/ai/history`)
          .catch(handleApiError);
        if (data && data.length > 0) {
          const history = data.map((conv) => ({
            role: conv.role,
            content: conv.content,
            id: conv.id,
            created_at: conv.created_at,
          }));
          setChatLog(history);
        }
      } catch (error) {
        console.error("Failed to load conversation history:", error);
      } finally {
        setLoadingHistory(false);
      }
    };

    loadHistory();
  }, [projectId, user?.id]);

  const sendMessage = async (event) => {
    event.preventDefault();
    if (!message.trim() || loading || !projectId) return;

    const userMessage = message.trim();
    setMessage("");

    // Add user message to chat log immediately
    const newUserMessage = {
      role: "user",
      content: userMessage,
      id: `local-${Date.now()}`,
      created_at: new Date().toISOString(),
    };
    setChatLog((prev) => [...prev, newUserMessage]);
    setLoading(true);

    try {
      const { data } = await apiClient
        .post(`/projects/${projectId}/ai/chat`, {
          message: userMessage,
        })
        .catch(handleApiError);

      const assistantEntry = {
        role: "assistant",
        content: data.reply || data.message || "I'm here to help!",
        id: data.id || `assistant-${Date.now()}`,
        created_at: new Date().toISOString(),
      };
      setChatLog((prev) => [...prev, assistantEntry]);
    } catch (error) {
      console.error(error);
      setChatLog((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
          id: `error-${Date.now()}`,
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="flex h-[80vh] flex-col">
      <CardHeader>
        <CardTitle>AI Assistant</CardTitle>
        <CardDescription>
          Chat with AI about your project, get help, and receive detailed, contextual suggestions.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-1 space-y-4 overflow-y-auto">
        {loadingHistory ? (
          <div className="flex h-full items-center justify-center">
            <p className="text-sm text-muted-foreground">
              Loading conversation history...
            </p>
          </div>
        ) : chatLog.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <p className="text-lg font-semibold">How can I help you today?</p>
              <p className="text-sm text-muted-foreground mt-2">
                Ask me about your project architecture, debugging issues, task
                planning, or implementation details.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {chatLog.map((entry) => (
              <div
                key={entry.id}
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
                  {entry.role === "user" ? (
                    <p className="text-sm whitespace-pre-wrap break-words">
                      {entry.content}
                    </p>
                  ) : (
                    <div className="text-sm prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown
                        components={{
                          code: ({ node, inline, className, children, ...props }) => {
                            const match = /language-(\w+)/.exec(className || "");
                            return !inline && match ? (
                              <pre className="bg-black/10 dark:bg-white/10 rounded p-3 overflow-x-auto my-2">
                                <code className={className} {...props}>
                                  {children}
                                </code>
                              </pre>
                            ) : (
                              <code className="bg-black/10 dark:bg-white/10 px-1.5 py-0.5 rounded text-xs" {...props}>
                                {children}
                              </code>
                            );
                          },
                          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                          ul: ({ children }) => <ul className="list-disc pl-4 mb-2">{children}</ul>,
                          ol: ({ children }) => <ol className="list-decimal pl-4 mb-2">{children}</ol>,
                          li: ({ children }) => <li className="mb-1">{children}</li>,
                          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                          em: ({ children }) => <em className="italic">{children}</em>,
                        }}
                      >
                        {entry.content}
                      </ReactMarkdown>
                    </div>
                  )}
                  {entry.created_at && (
                    <p className={`mt-1 text-[10px] text-muted-foreground ${entry.role === "user" ? "text-right" : "text-left"}`}>
                      {new Date(entry.created_at).toLocaleTimeString()}
                    </p>
                  )}
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
                    <div
                      className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    />
                    <div
                      className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    />
                    <div
                      className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    />
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
            placeholder={
              projectId
                ? "Ask about this project's code, tasks, or architecture..."
                : "Select a project to start chatting..."
            }
            disabled={loading || !projectId}
            className="flex-1"
          />
          <Button type="submit" disabled={loading || !message.trim() || !projectId}>
            {loading ? "Sending..." : "Send"}
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}

