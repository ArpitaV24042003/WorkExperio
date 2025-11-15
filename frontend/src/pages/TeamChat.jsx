import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { apiClient, handleApiError } from "../lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";

export default function TeamChat() {
  const { projectId } = useParams();
  const { user } = useAuthStore();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const socketRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load previous messages
  useEffect(() => {
    const loadMessages = async () => {
      try {
        const { data } = await apiClient.get(`/chat/projects/${projectId}/messages`).catch(handleApiError);
        setMessages(data || []);
      } catch (error) {
        console.error("Failed to load messages:", error);
      } finally {
        setLoading(false);
      }
    };
    loadMessages();
  }, [projectId]);

  // WebSocket connection
  useEffect(() => {
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsHost = import.meta.env.VITE_WS_URL?.replace(/^https?:\/\//, "") || "localhost:8000";
    const socketUrl = `${wsProtocol}//${wsHost}/ws/projects/${projectId}/chat`;
    const socket = new WebSocket(socketUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      setConnected(true);
      console.info("Chat connected");
    };

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.error) {
        console.error("Chat error:", message.error);
        return;
      }
      setMessages((prev) => [...prev, message]);
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      setConnected(false);
    };

    socket.onclose = () => {
      console.info("Chat disconnected");
      setConnected(false);
    };

    return () => {
      socket.close();
    };
  }, [projectId]);

  const sendMessage = (event) => {
    event.preventDefault();
    if (!input.trim() || !connected) return;
    socketRef.current?.send(
      JSON.stringify({
        user_id: user?.id,
        content: input.trim(),
      })
    );
    setInput("");
  };

  return (
    <Card className="flex h-[70vh] flex-col">
      <CardHeader>
        <CardTitle>Team chat</CardTitle>
        <CardDescription>
          Coordinate tasks, unblock teammates, and capture decisions.
          {connected ? (
            <span className="ml-2 text-green-600">● Connected</span>
          ) : (
            <span className="ml-2 text-red-600">● Disconnected</span>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-1 space-y-4 overflow-y-auto">
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading messages...</p>
        ) : messages.length === 0 ? (
          <p className="text-sm text-muted-foreground">No messages yet. Start the conversation!</p>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`rounded-md border p-3 ${
                message.user_id === user?.id ? "ml-auto w-[80%] bg-primary/10" : "mr-auto w-[80%] bg-background"
              }`}
            >
              <p className="text-sm font-semibold">{message.user_id === user?.id ? "You" : message.user_id}</p>
              <p className="text-sm">{message.content}</p>
              <p className="text-[10px] text-muted-foreground">
                {new Date(message.created_at ?? Date.now()).toLocaleTimeString()}
              </p>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </CardContent>
      <CardFooter>
        <form className="flex w-full gap-2" onSubmit={sendMessage}>
          <Input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder={connected ? "Type a message..." : "Connecting..."}
            disabled={!connected}
          />
          <Button type="submit" disabled={!connected || !input.trim()}>
            Send
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}

