# from fastapi import APIRouter
# from app.mongo import save_chat_message, get_chat_history

# router = APIRouter(prefix="/chat", tags=["Chat"])

# @router.post("/send")
# def send_message(user_name: str, message: str):
#     save_chat_message(user_name, message)
#     return {"status": "sent"}

# @router.get("/history")
# def chat_history():
#     return get_chat_history()


# routers/chatbot.py
from fastapi import APIRouter, Query
from typing import List

router = APIRouter()

chat_history: List[dict] = []

@router.post("/send")
def send_message(user_name: str = Query(...), message: str = Query(...)):
    chat_history.append({"user": user_name, "message": message})
    return {"status": "sent"}

@router.get("/history")
def get_history():
    return chat_history
