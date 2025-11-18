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
        // Load messages (ordered oldest to newest for chat display)
        const { data } = await apiClient.get(`/chat/projects/${projectId}/messages`, {
          params: { limit: 100 }
        }).catch(handleApiError);
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
    <Card className="flex h-[80vh] flex-col bg-background">
      <CardHeader className="border-b bg-muted/50 pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground font-semibold">
              T
            </div>
            <div>
              <CardTitle className="text-lg">Team Chat</CardTitle>
              <CardDescription className="text-xs">
                {connected ? (
                  <span className="text-green-600">● Online</span>
                ) : (
                  <span className="text-red-600">● Offline</span>
                )}
                {onlineUsers.size > 0 && (
                  <span className="ml-2">{onlineUsers.size} member{onlineUsers.size !== 1 ? "s" : ""} online</span>
                )}
              </CardDescription>
            </div>
          </div>
        </div>
        {/* Typing indicator */}
        {typingUsers.size > 0 && (
          <div className="mt-2 text-xs text-muted-foreground italic animate-pulse">
            {Array.from(typingUsers)
              .map((userId) => userNames[userId] || userId)
              .filter(Boolean)
              .join(", ")}{" "}
            {typingUsers.size === 1 ? "is" : "are"} typing...
          </div>
        )}
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-3 bg-gradient-to-b from-background to-muted/20">
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading messages...</p>
        ) : messages.length === 0 ? (
          <p className="text-sm text-muted-foreground">No messages yet. Start the conversation!</p>
        ) : (
          messages.map((message, index) => {
            const senderName = userNames[message.user_id] || message.user_id;
            const isCurrentUser = message.user_id === user?.id;
            const isOnline = onlineUsers.has(message.user_id);
            const prevMessage = index > 0 ? messages[index - 1] : null;
            const showAvatar = !prevMessage || prevMessage.user_id !== message.user_id;
            const messageTime = new Date(message.created_at ?? Date.now());
            const showTime = !prevMessage || 
              Math.abs(new Date(prevMessage.created_at ?? Date.now()).getTime() - messageTime.getTime()) > 300000; // 5 minutes
            
            return (
              <div key={message.id}>
                {showTime && (
                  <div className="flex justify-center my-4">
                    <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded-full">
                      {messageTime.toLocaleDateString() === new Date().toLocaleDateString()
                        ? `Today, ${messageTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
                        : messageTime.toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                    </span>
                  </div>
                )}
                <div
                  className={`flex gap-2 items-end ${
                    isCurrentUser ? "justify-end" : "justify-start"
                  } ${showAvatar ? "mt-2" : "mt-1"}`}
                >
                  {!isCurrentUser && (
                    <div className="flex flex-col items-center shrink-0">
                      {showAvatar ? (
                        <>
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/20 text-sm font-semibold border-2 border-primary/30">
                            {senderName.charAt(0).toUpperCase()}
                          </div>
                          {isOnline && (
                            <span className="h-2.5 w-2.5 rounded-full bg-green-500 -mt-2 border-2 border-background"></span>
                          )}
                        </>
                      ) : (
                        <div className="h-10 w-10"></div>
                      )}
                    </div>
                  )}
                  <div
                    className={`rounded-2xl px-4 py-2.5 max-w-[75%] shadow-sm ${
                      isCurrentUser
                        ? "bg-primary text-primary-foreground rounded-br-md"
                        : "bg-muted text-foreground rounded-bl-md"
                    }`}
                  >
                    {!isCurrentUser && showAvatar && (
                      <p className="text-xs font-semibold mb-1.5 opacity-90">{senderName}</p>
                    )}
                    <p className="text-sm break-words whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    <p className={`text-[10px] mt-1.5 ${isCurrentUser ? "opacity-80" : "opacity-60"}`}>
                      {messageTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  {isCurrentUser && (
                    <div className="flex flex-col items-center shrink-0">
                      {showAvatar ? (
                        <>
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary text-sm font-semibold border-2 border-secondary/50">
                            You
                          </div>
                          {isOnline && (
                            <span className="h-2.5 w-2.5 rounded-full bg-green-500 -mt-2 border-2 border-background"></span>
                          )}
                        </>
                      ) : (
                        <div className="h-10 w-10"></div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </CardContent>
      <CardFooter className="border-t bg-muted/30 p-3">
        <form className="flex w-full gap-2 items-end" onSubmit={sendMessage}>
          <div className="flex-1 relative">
            <Input
              value={input}
              onChange={handleInputChange}
              placeholder={connected ? "Type a message..." : "Connecting..."}
              disabled={!connected}
              className="pr-12 rounded-full bg-background border-2 focus:border-primary"
              onKeyPress={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage(e);
                }
              }}
            />
          </div>
          <Button 
            type="submit" 
            disabled={!connected || !input.trim()}
            className="rounded-full h-10 w-10 p-0"
            size="icon"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="h-5 w-5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L6 12zm0 0h8.5" />
            </svg>
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}

