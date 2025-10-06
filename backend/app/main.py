import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# This structure helps ensure all modules are found correctly
# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base, engine
from app.routers import (
    mongo_routes,
    projects,
    users,
    resumes,
    chatbot,
    teams,
)

# This is the new, robust way to handle startup tasks.
# It is guaranteed to run BEFORE the application starts accepting requests.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on server startup
    print("Application startup: Creating database tables...")
    # Use a try-except block for safety
    try:
        Base.metadata.create_all(bind=engine)
        print("Application startup: Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
    
    yield
    
    # This code runs on server shutdown
    print("Application shutdown.")

# We pass the new lifespan function to the FastAPI app
app = FastAPI(title="WorkExperio API", lifespan=lifespan)

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

