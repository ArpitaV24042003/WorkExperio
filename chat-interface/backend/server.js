// chat-interface/backend/server.js
import { createServer } from "node:http";
import express from "express";
import { Server } from "socket.io";

const app = express();

// simple health + root
app.get("/", (_req, res) => res.send("<h1>Chat interface up</h1>"));
app.get("/health", (_req, res) => res.json({ status: "ok" }));

const server = createServer(app);

// NOTE: in production, set origin to your deployed chat-frontend URL
const io = new Server(server, {
  cors: {
    origin: "*",               // e.g. "https://<your-chat-frontend>.onrender.com"
    methods: ["GET", "POST"],
  },
});

const ROOM = "group";

io.on("connection", (socket) => {
  console.log("a user connected", socket.id);

  socket.on("joinRoom", async (userName) => {
    console.log(`${userName} is joining the group.`);
    await socket.join(ROOM);
    // notify others that someone joined
    socket.to(ROOM).emit("roomNotice", userName);
  });

  socket.on("chatMessage", (msg) => {
    // send message to everyone in the room except sender
    socket.to(ROOM).emit("chatMessage", msg);
  });

  socket.on("typing", (userName) => {
    socket.to(ROOM).emit("typing", userName);
  });

  socket.on("stopTyping", (userName) => {
    socket.to(ROOM).emit("stopTyping", userName);
  });

  socket.on("disconnect", () => {
    console.log("user disconnected", socket.id);
  });
});

// IMPORTANT: use Render's PORT and 0.0.0.0
const PORT = process.env.PORT || 3001;
server.listen(PORT, "0.0.0.0", () => {
  console.log(`✅ server running on ${PORT}`);
});
