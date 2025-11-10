from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

# ---------------------------
# Load environment variables
# ---------------------------
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

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
# (This is a good use for Mongo)
# ---------------------------
resume_raw = mongo_db["resume_raw"]        # Stores original extracted text
resume_parsed = mongo_db["resume_parsed"]  # Stores structured AI parsed output

# ---------------------------
# Logs and analysis collections
# (This is a good use for Mongo)
# ---------------------------
chat_logs = mongo_db["chat_logs"]
ai_evaluation = mongo_db["ai_evaluation"]
team_suggestions = mongo_db["team_suggestions"]
skill_extraction_logs = mongo_db["skill_extraction_logs"]
evaluation_logs = mongo_db["evaluation_logs"]

# ---------------------------
# REMOVED: Redundant Structured collections
# ---------------------------
# The following collections were removed because this data is now stored
# in your PostgreSQL database using the SQLAlchemy models:
# - education
# - experience
# - projects
# - certificates

# ---------------------------
# REMOVED: Chatbot collection & functions
# ---------------------------
# This logic was moved to your PostgreSQL database (models.ChatRoom,
# models.ChatMessage) and is handled by your FastAPI routers.
# - chat_messages (collection)
# - save_chat_message (function)
# - get_chat_history (function)

# ---------------------------
# Main entry
# ---------------------------
if __name__ == "__main__":
    print("MongoDB connection and collections initialized successfully.")
    print("Note: Chat and resume-part collections (education, projects, etc.)")
    print("are now handled by PostgreSQL.")