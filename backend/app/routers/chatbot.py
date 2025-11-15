# # from fastapi import APIRouter
# # from app.mongo import save_chat_message, get_chat_history

# # router = APIRouter(prefix="/chat", tags=["Chat"])

# # @router.post("/send")
# # def send_message(user_name: str, message: str):
# #     save_chat_message(user_name, message)
# #     return {"status": "sent"}

# # @router.get("/history")
# # def chat_history():
# #     return get_chat_history()


# # routers/chatbot.py
# from fastapi import APIRouter, Query
# from typing import List

# router = APIRouter(tags=["Chat"])

# chat_history: List[dict] = []

# @router.post("/send")
# def send_message(user_name: str = Query(...), message: str = Query(...)):
#     chat_history.append({"user": user_name, "message": message})
#     return {"status": "sent"}

# @router.get("/history")
# def get_history():
#     return chat_history



from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from .. import models # NEW
from ..db import get_db # NEW

router = APIRouter(tags=["Chat"])

# --- NEW SCHEMAS ---
# (You should move these to schemas.py)
class MessageCreate(BaseModel):
    content: str
    user_id: int

class MessageOut(BaseModel):
    id: int
    content: str
    user_id: int
    room_id: int
    timestamp: str 
    
    class Config:
        orm_mode = True
        # Format timestamp for JSON output
        json_encoders = {
            models.ChatMessage.timestamp: lambda v: v.isoformat() if v else None
        }

#
# --- ENDPOINTS (REWRITTEN) ---
#
@router.post("/rooms/{room_id}/send", response_model=MessageOut)
def send_message(
    room_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Send a message to a specific chat room.
    """
    # Check if room and user exist
    db_room = db.query(models.ChatRoom).filter(models.ChatRoom.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
        
    db_user = db.query(models.User).filter(models.User.id == message.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create the chat message
    db_message = models.ChatMessage(
        content=message.content,
        user_id=message.user_id,
        room_id=room_id
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return db_message

@router.get("/rooms/{room_id}/history", response_model=List[MessageOut])
def get_history(
    room_id: int, 
    db: Session = Depends(get_db),
    limit: int = Query(50, gt=0, le=100) # Add pagination
):
    """
    Get the chat history for a specific room.
    """
    db_room = db.query(models.ChatRoom).filter(models.ChatRoom.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
        
    # Query for messages, order by most recent, and limit the count
    messages = db.query(models.ChatMessage)\
        .filter(models.ChatMessage.room_id == room_id)\
        .order_by(models.ChatMessage.timestamp.desc())\
        .limit(limit)\
        .all()
        
    # Return in chronological order (oldest first)
    return list(reversed(messages))
