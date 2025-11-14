from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from ..db import get_db
from ..models import ChatMessage

router = APIRouter()

active_connections: Dict[str, List[WebSocket]] = {}


async def broadcast(project_id: str, message: dict):
	for connection in active_connections.get(project_id, []):
		await connection.send_json(message)


@router.websocket("/ws/projects/{project_id}/chat")
async def project_chat(websocket: WebSocket, project_id: str, db: Session = Depends(get_db)):
	await websocket.accept()
	connections = active_connections.setdefault(project_id, [])
	connections.append(websocket)
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
	finally:
		connections.remove(websocket)
		if not connections:
			active_connections.pop(project_id, None)

