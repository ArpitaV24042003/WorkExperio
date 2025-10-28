import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine, Base
import app.models 

# --- Debugging: Print database URL ---
print("=" * 60)
print(f"DATABASE URL AT RUNTIME: {os.getenv('DATABASE_URL')}")
print("=" * 60)

# --- Add app folder to sys.path ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- Import routers ---
from app.routers import (
    users,
    resumes,
    mongo_routes,
    chatbot,
    teams,
    projects,
)

# --- Initialize FastAPI App ---
app = FastAPI(
    title="WorkExperio API",
    version="0.1.0",
    description="Backend API for WorkExperio — AI-driven Team Formation & Performance Analysis",
    servers=[
        {"url": "http://127.0.0.1:8000", "description": "Local development server"}
    ]
)

# --- Enable CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace * with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Root Endpoint ---
@app.get("/")
def root():
    return {"status": "ok", "service": "WorkExperio Backend"}

# --- Database Health Check ---
@app.get("/db-check")
def check_db_tables():
    """
    Check PostgreSQL connection and verify if 'users' table exists.
    """
    try:
        with engine.connect() as connection:
            query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """)
            result = connection.execute(query).scalar()
            return {"message": "Database connection successful", "users_table_exists": result}
    except Exception as e:
        return {"error": "Failed to connect or query database", "details": str(e)}

# --- Include Routers ---
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
app.include_router(mongo_routes.router, prefix="/mongo", tags=["MongoDB"])
app.include_router(chatbot.router, prefix="/chat", tags=["Chat"])
app.include_router(teams.router, prefix="/teams", tags=["Teams"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])

# --- Create tables if they don’t exist ---
print("Creating database tables (if not exist)...")
Base.metadata.create_all(bind=engine)
print("✅ Database setup complete.")

# --- Run this if executed directly ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
