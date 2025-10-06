from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

# ---------------------------
# Load environment variables
# ---------------------------
load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL")
MONGO_DB_NAME = os.getenv("MONGODB_DB")

# ---------------------------
# Connect to MongoDB
# ---------------------------
client = MongoClient(MONGO_URL)
mongo_db = client[MONGO_DB_NAME]

print("✅ Connected to MongoDB successfully!")
print("Databases:", client.list_database_names())
print("Collections in", MONGO_DB_NAME, ":", mongo_db.list_collection_names())

# ---------------------------
# Resume collections
# ---------------------------
resume_raw = mongo_db["resume_raw"]          # Stores original extracted text
resume_parsed = mongo_db["resume_parsed"]    # Stores structured AI parsed output

# ---------------------------
# Structured collections
# ---------------------------
education = mongo_db["education"]
experience = mongo_db["experience"]
projects = mongo_db["projects"]
certificates = mongo_db["certificates"]

# ---------------------------
# Logs and analysis collections
# ---------------------------
chat_logs = mongo_db["chat_logs"]
ai_evaluation = mongo_db["ai_evaluation"]
team_suggestions = mongo_db["team_suggestions"]
skill_extraction_logs = mongo_db["skill_extraction_logs"]
evaluation_logs = mongo_db["evaluation_logs"]

# ---------------------------
# 🧠 Chatbot collection
# ---------------------------
chat_messages = mongo_db["chat_messages"]

# ---------------------------
# 🧩 Chatbot helper functions
# ---------------------------
def save_chat_message(user_name: str, message: str, timestamp: datetime = None):
    """
    Save a chat message to MongoDB.
    """
    if not user_name or not message:
        raise ValueError("user_name and message are required fields.")
    
    if timestamp is None:
        timestamp = datetime.utcnow()
        
    chat_messages.insert_one({
        "user_name": user_name,
        "message": message,
        "timestamp": timestamp
    })
    print(f"💬 [Saved] {user_name}: {message}")


def get_chat_history(limit: int = 50):
    """
    Retrieve the latest chat messages (oldest first).
    """
    messages = list(chat_messages.find().sort("timestamp", -1).limit(limit))
    messages.reverse()
    return messages

# ---------------------------
# Main entry (no dummy inserts)
# ---------------------------
if __name__ == "__main__":
    print("MongoDB connection and collections initialized successfully.")
