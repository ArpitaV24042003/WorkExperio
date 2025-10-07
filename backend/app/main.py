import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ADD THIS PRINT STATEMENT
print("="*50)
print(f"DATABASE URL AT RUNTIME: {os.getenv('DATABASE_URL')}")
print("="*50)

# This structure helps ensure all modules are found correctly
# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.routers import (
    mongo_routes,
    projects,
    users,
    resumes,
    chatbot,
    teams,
)

# No lifespan function is needed here, as Alembic will handle the database setup.
app = FastAPI(title="WorkExperio API")

# Enable CORS so your React frontend can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all your routers
app.include_router(mongo_routes.router, prefix="/mongo")
app.include_router(users.router, prefix="/users")
app.include_router(resumes.router, prefix="/resumes")
app.include_router(chatbot.router, prefix="/chat")
app.include_router(teams.router, prefix="/teams")
app.include_router(projects.router, prefix="/projects")

# Health check endpoint
@app.get("/")
def root():
    return {"status": "ok", "service": "WorkExperio Backend"}

