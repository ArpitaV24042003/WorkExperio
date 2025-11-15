from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from ..db import get_db
from ..models import ChatMessage

router = APIRouter()

active_connections: Dict[str, List[WebSocket]] = {}


async def broadcast(project_id: str, message: dict):
	for connection in active_connections.get(project_id, []):
		await connection.send_json(message)


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
	connections = active_connections.setdefault(project_id, [])
	connections.append(websocket)
	
	# Create a database session for this WebSocket connection
	from ..db import SessionLocal
	db = SessionLocal()
	
	try:
		while True:
			data = await websocket.receive_json()
			user_id = data.get("user_id")
			content = data.get("content")
			if not user_id or not content:
				await websocket.send_json({"error": "Invalid payload"})
				continue
			message = ChatMessage(project_id=project_id, user_id=user_id, content=content)
			db.add(message)
			db.commit()
			db.refresh(message)
			await broadcast(
				project_id,
				{
					"id": message.id,
					"user_id": user_id,
					"content": content,
					"created_at": message.created_at.isoformat(),
				},
			)
	except WebSocketDisconnect:
		pass
	except Exception as e:
		print(f"WebSocket error: {e}")
	finally:
		db.close()
		connections.remove(websocket)
		if not connections:
			active_connections.pop(project_id, None)

