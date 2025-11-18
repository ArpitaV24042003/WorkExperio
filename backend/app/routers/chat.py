from typing import Dict, List, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..db import get_db
from ..models import ChatMessage

router = APIRouter()

active_connections: Dict[str, List[WebSocket]] = {}  # project_id -> list of websockets
user_connections: Dict[str, Dict[str, WebSocket]] = {}  # project_id -> {user_id: websocket}
typing_users: Dict[str, Dict[str, datetime]] = {}  # project_id -> {user_id: last_typing_time}
online_users: Dict[str, Set[str]] = {}  # project_id -> set of user_ids


async def broadcast(project_id: str, message: dict):
	"""Broadcast message to all connections in a project"""
	for connection in active_connections.get(project_id, []):
		try:
			await connection.send_json(message)
		except Exception as e:
			print(f"Error broadcasting to connection: {e}")


async def broadcast_to_others(project_id: str, exclude_user_id: str, message: dict):
	"""Broadcast message to all connections except the sender"""
	if project_id not in user_connections:
		return
	
	for user_id, connection in user_connections[project_id].items():
		if user_id != exclude_user_id:
			try:
				await connection.send_json(message)
			except Exception as e:
				print(f"Error broadcasting to user {user_id}: {e}")


@router.get("/projects/{project_id}/messages")
def get_messages(project_id: str, db: Session = Depends(get_db), limit: int = 100):
	"""Fetch previous chat messages for a project"""
	messages = (
		db.query(ChatMessage)
		.filter(ChatMessage.project_id == project_id)
		.order_by(ChatMessage.created_at.desc())
		.limit(limit)
		.all()
	)
	# Reverse to show oldest first (for proper chat history display)
	messages = list(reversed(messages))
	return [
		{
			"id": msg.id,
			"user_id": msg.user_id,
			"content": msg.content,
			"created_at": msg.created_at.isoformat(),
		}
		for msg in reversed(messages)
	]


@router.websocket("/ws/projects/{project_id}/chat")
async def project_chat(websocket: WebSocket, project_id: str):
	await websocket.accept()
	
	# Get user_id from initial connection message
	user_id = None
	try:
		initial_data = await websocket.receive_json()
		user_id = initial_data.get("user_id")
		if not user_id:
			await websocket.close(code=1008, reason="user_id required")
			return
	except Exception as e:
		print(f"Error getting user_id: {e}")
		await websocket.close(code=1008, reason="Invalid initial message")
		return
	
	# Register connection
	connections = active_connections.setdefault(project_id, [])
	connections.append(websocket)
	
	project_users = user_connections.setdefault(project_id, {})
	project_users[user_id] = websocket
	
	# Add to online users
	online = online_users.setdefault(project_id, set())
	online.add(user_id)
	
	# Notify others that user is online
	await broadcast_to_others(
		project_id,
		user_id,
		{
			"type": "user_online",
			"user_id": user_id,
			"online_users": list(online),
		},
	)
	
	# Send current online users to the new connection
	await websocket.send_json({
		"type": "online_users",
		"online_users": list(online),
	})
	
	# Create a database session for this WebSocket connection
	from ..db import SessionLocal
	db = SessionLocal()
	
	typing_timeout = timedelta(seconds=3)  # Stop showing typing after 3 seconds
	
	try:
		while True:
			data = await websocket.receive_json()
			message_type = data.get("type", "message")
			
			if message_type == "message":
				content = data.get("content")
				if not content:
					await websocket.send_json({"error": "Content required"})
					continue
				
				# Save message to database
				message = ChatMessage(project_id=project_id, user_id=user_id, content=content)
				db.add(message)
				db.commit()
				db.refresh(message)
				
				# Broadcast message
				await broadcast(
					project_id,
					{
						"type": "message",
						"id": message.id,
						"user_id": user_id,
						"content": content,
						"created_at": message.created_at.isoformat(),
					},
				)
				
				# Clear typing indicator
				if project_id in typing_users and user_id in typing_users[project_id]:
					del typing_users[project_id][user_id]
					await broadcast_to_others(
						project_id,
						user_id,
						{
							"type": "typing_stopped",
							"user_id": user_id,
						},
					)
			
			elif message_type == "typing":
				# Update typing status
				project_typing = typing_users.setdefault(project_id, {})
				project_typing[user_id] = datetime.utcnow()
				
				# Notify others
				await broadcast_to_others(
					project_id,
					user_id,
					{
						"type": "typing",
						"user_id": user_id,
					},
				)
			
			elif message_type == "typing_stopped":
				# Clear typing indicator
				if project_id in typing_users and user_id in typing_users[project_id]:
					del typing_users[project_id][user_id]
					await broadcast_to_others(
						project_id,
						user_id,
						{
							"type": "typing_stopped",
							"user_id": user_id,
						},
					)
	
	except WebSocketDisconnect:
		pass
	except Exception as e:
		print(f"WebSocket error: {e}")
	finally:
		# Clean up
		if project_id in user_connections and user_id in user_connections[project_id]:
			del user_connections[project_id][user_id]
		
		if project_id in online_users:
			online_users[project_id].discard(user_id)
			# Notify others that user went offline
			await broadcast_to_others(
				project_id,
				user_id,
				{
					"type": "user_offline",
					"user_id": user_id,
					"online_users": list(online_users[project_id]),
				},
			)
		
		if project_id in typing_users and user_id in typing_users[project_id]:
			del typing_users[project_id][user_id]
		
		if websocket in connections:
			connections.remove(websocket)
		
		if not connections:
			active_connections.pop(project_id, None)
			user_connections.pop(project_id, None)
			typing_users.pop(project_id, None)
			online_users.pop(project_id, None)
		
		db.close()

