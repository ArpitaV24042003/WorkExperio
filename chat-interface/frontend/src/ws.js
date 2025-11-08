import { io } from "socket.io-client";

// Use .env variable if available, otherwise default to localhost for local dev
const CHAT_URL = import.meta.env.VITE_CHAT_URL || "http://localhost:4600";

/**
 * Connect to the WebSocket (Socket.IO) server.
 * Works both locally and in production.
 */
export function connectWS() {
  const socket = io(CHAT_URL, {
    transports: ["websocket"], // faster and stable on Render
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1000,
    withCredentials: false,
  });

  socket.on("connect", () => console.log("[ws] connected:", socket.id));
  socket.on("disconnect", (reason) =>
    console.log("[ws] disconnected:", reason)
  );
  socket.on("connect_error", (err) =>
    console.warn("[ws] connection error:", err.message)
  );

  return socket;
}
