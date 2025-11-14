import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";

export default function TeamChat() {
  const { projectId } = useParams();
  const { user } = useAuthStore();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const socketRef = useRef(null);

  useEffect(() => {
    const socketUrl = (import.meta.env.VITE_WS_URL ?? "ws://localhost:8000") + `/ws/projects/${projectId}/chat`;
    const socket = new WebSocket(socketUrl);
    socketRef.current = socket;

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.error) return;
      setMessages((prev) => [...prev, message]);
    };

    socket.onclose = () => {
      console.info("Chat disconnected");
    };

    return () => {
      socket.close();
    };
  }, [projectId]);

  const sendMessage = (event) => {
    event.preventDefault();
    if (!input.trim()) return;
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
        <CardDescription>Coordinate tasks, unblock teammates, and capture decisions.</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 space-y-4 overflow-y-auto">
        {messages.length === 0 ? (
          <p className="text-sm text-muted-foreground">No messages yet. Start the conversation!</p>
        ) : (
          messages.map((message) => (
            <div key={message.id} className="rounded-md border bg-background p-3">
              <p className="text-sm font-semibold">{message.user_id}</p>
              <p className="text-sm">{message.content}</p>
              <p className="text-[10px] text-muted-foreground">
                {new Date(message.created_at ?? Date.now()).toLocaleTimeString()}
              </p>
            </div>
          ))
        )}
      </CardContent>
      <CardFooter>
        <form className="flex w-full gap-2" onSubmit={sendMessage}>
          <Input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Type a message..." />
          <Button type="submit">Send</Button>
        </form>
      </CardFooter>
    </Card>
  );
}

