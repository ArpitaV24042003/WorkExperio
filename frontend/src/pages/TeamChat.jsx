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
  const [userNames, setUserNames] = useState({}); // Map user_id to name
  const [typingUsers, setTypingUsers] = useState(new Set()); // Set of user_ids who are typing
  const [onlineUsers, setOnlineUsers] = useState(new Set()); // Set of user_ids who are online
  const socketRef = useRef(null);
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load previous messages and team members
  useEffect(() => {
    const loadData = async () => {
      try {
        // Load messages
        const { data } = await apiClient.get(`/chat/projects/${projectId}/messages`).catch(handleApiError);
        setMessages(data || []);
        
        // Load team members to get names
        try {
          const teamData = await apiClient.get(`/teams/projects/${projectId}/team`).catch(handleApiError);
          const members = teamData.data.members || [];
          const nameMap = {};
          
          // Fetch user details for each member
          for (const member of members) {
            try {
              const userData = await apiClient.get(`/users/${member.user_id}/profile`).catch(() => null);
              if (userData?.data) {
                nameMap[member.user_id] = userData.data.name || member.user_id;
              }
            } catch {
              nameMap[member.user_id] = member.user_id;
            }
          }
          
          // Add current user
          if (user?.id) {
            try {
              const userData = await apiClient.get(`/users/${user.id}/profile`).catch(() => null);
              if (userData?.data) {
                nameMap[user.id] = userData.data.name || user.id;
              }
            } catch {
              nameMap[user.id] = user.id;
            }
          }
          
          setUserNames(nameMap);
        } catch (err) {
          console.error("Failed to load team:", err);
        }
      } catch (error) {
        console.error("Failed to load messages:", error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [projectId, user?.id]);

  // WebSocket connection
  useEffect(() => {
    if (!user?.id) return;
    
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    const wsProtocol = apiUrl.startsWith("https") ? "wss:" : "ws:";
    const wsHost = apiUrl.replace(/^https?:\/\//, "").replace(/\/$/, ""); // Remove http/https and trailing slash
    const socketUrl = `${wsProtocol}//${wsHost}/ws/projects/${projectId}/chat`;
    
    console.log("Connecting to WebSocket:", socketUrl);
    const socket = new WebSocket(socketUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      // Send user_id as initial message
      socket.send(JSON.stringify({ user_id: user.id }));
      setConnected(true);
      console.info("Chat connected");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.error) {
        console.error("Chat error:", data.error);
        return;
      }
      
      const messageType = data.type || "message";
      
      if (messageType === "message") {
        setMessages((prev) => [...prev, data]);
      } else if (messageType === "typing") {
        setTypingUsers((prev) => new Set([...prev, data.user_id]));
        // Auto-clear typing after 3 seconds
        setTimeout(() => {
          setTypingUsers((prev) => {
            const newSet = new Set(prev);
            newSet.delete(data.user_id);
            return newSet;
          });
        }, 3000);
      } else if (messageType === "typing_stopped") {
        setTypingUsers((prev) => {
          const newSet = new Set(prev);
          newSet.delete(data.user_id);
          return newSet;
        });
      } else if (messageType === "user_online" || messageType === "online_users") {
        setOnlineUsers(new Set(data.online_users || []));
      } else if (messageType === "user_offline") {
        setOnlineUsers(new Set(data.online_users || []));
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      setConnected(false);
    };

    socket.onclose = () => {
      console.info("Chat disconnected");
      setConnected(false);
      setOnlineUsers(new Set());
      setTypingUsers(new Set());
    };

    return () => {
      socket.close();
    };
  }, [projectId, user?.id]);

  const handleInputChange = (e) => {
    setInput(e.target.value);
    
    // Send typing indicator
    if (connected && socketRef.current) {
      socketRef.current.send(
        JSON.stringify({
          type: "typing",
          user_id: user?.id,
        })
      );
      
      // Clear previous timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      
      // Stop typing indicator after 2 seconds of no typing
      typingTimeoutRef.current = setTimeout(() => {
        if (socketRef.current && connected) {
          socketRef.current.send(
            JSON.stringify({
              type: "typing_stopped",
              user_id: user?.id,
            })
          );
        }
      }, 2000);
    }
  };

  const sendMessage = (event) => {
    event.preventDefault();
    if (!input.trim() || !connected) return;
    
    // Clear typing indicator
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    if (socketRef.current && connected) {
      socketRef.current.send(
        JSON.stringify({
          type: "typing_stopped",
          user_id: user?.id,
        })
      );
    }
    
    socketRef.current?.send(
      JSON.stringify({
        type: "message",
        user_id: user?.id,
        content: input.trim(),
      })
    );
    setInput("");
  };

  return (
    <Card className="flex h-[70vh] flex-col">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Team chat</CardTitle>
            <CardDescription>
              Coordinate tasks, unblock teammates, and capture decisions.
              {connected ? (
                <span className="ml-2 text-green-600">● Connected</span>
              ) : (
                <span className="ml-2 text-red-600">● Disconnected</span>
              )}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {/* Online users indicator */}
            {onlineUsers.size > 0 && (
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <span className="h-2 w-2 rounded-full bg-green-500"></span>
                <span>{onlineUsers.size} online</span>
              </div>
            )}
          </div>
        </div>
        {/* Typing indicator */}
        {typingUsers.size > 0 && (
          <div className="mt-2 text-sm text-muted-foreground italic">
            {Array.from(typingUsers)
              .map((userId) => userNames[userId] || userId)
              .filter(Boolean)
              .join(", ")}{" "}
            {typingUsers.size === 1 ? "is" : "are"} typing...
          </div>
        )}
      </CardHeader>
      <CardContent className="flex-1 space-y-4 overflow-y-auto">
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading messages...</p>
        ) : messages.length === 0 ? (
          <p className="text-sm text-muted-foreground">No messages yet. Start the conversation!</p>
        ) : (
          messages.map((message) => {
            const senderName = userNames[message.user_id] || message.user_id;
            const isCurrentUser = message.user_id === user?.id;
            const isOnline = onlineUsers.has(message.user_id);
            return (
              <div
                key={message.id}
                className={`flex gap-2 ${
                  isCurrentUser ? "justify-end" : "justify-start"
                }`}
              >
                {!isCurrentUser && (
                  <div className="flex flex-col items-center">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold">
                      {senderName.charAt(0).toUpperCase()}
                    </div>
                    {isOnline && (
                      <span className="h-2 w-2 rounded-full bg-green-500 -mt-1 border-2 border-background"></span>
                    )}
                  </div>
                )}
                <div
                  className={`rounded-lg px-4 py-2 max-w-[70%] ${
                    isCurrentUser
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  {!isCurrentUser && (
                    <p className="text-xs font-semibold mb-1">{senderName}</p>
                  )}
                  <p className="text-sm break-words whitespace-pre-wrap">{message.content}</p>
                  <p className="text-[10px] opacity-70 mt-1">
                    {new Date(message.created_at ?? Date.now()).toLocaleTimeString()}
                  </p>
                </div>
                {isCurrentUser && (
                  <div className="flex flex-col items-center">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary text-sm font-semibold">
                      You
                    </div>
                    {isOnline && (
                      <span className="h-2 w-2 rounded-full bg-green-500 -mt-1 border-2 border-background"></span>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </CardContent>
      <CardFooter>
        <form className="flex w-full gap-2" onSubmit={sendMessage}>
          <Input
            value={input}
            onChange={handleInputChange}
            placeholder={connected ? "Type a message..." : "Connecting..."}
            disabled={!connected}
            onKeyPress={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage(e);
              }
            }}
          />
          <Button type="submit" disabled={!connected || !input.trim()}>
            Send
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}

