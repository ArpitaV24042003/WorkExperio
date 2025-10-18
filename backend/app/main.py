import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .database import engine 

# --- Debugging ---
# Print the database URL when the application starts
print("="*50)
print(f"DATABASE URL AT RUNTIME: {os.getenv('DATABASE_URL')}")
print("="*50)

# --- Router Imports ---
# This assumes your project structure is correct
from app.routers import (
    mongo_routes,
    projects,
    users,
    resumes,
    chatbot,
    teams,
)

# --- FastAPI App Initialization (Happens Only ONCE) ---
app = FastAPI(title="WorkExperio API")

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Diagnostic Endpoint ---
@app.get("/db-check")
def check_db_tables():
    try:
        with engine.connect() as connection:
            # Query to check if the 'users' table exists
            query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """)
            result = connection.execute(query).scalar()
            return {"message": "Database check successful", "users_table_exists": result}
    except Exception as e:
        # Return the actual database error if the connection fails
        return {"error": "Failed to connect or query database", "details": str(e)}

# --- Register Routers ---
app.include_router(mongo_routes.router, prefix="/mongo")
app.include_router(users.router, prefix="/users")
app.include_router(resumes.router, prefix="/resumes")
app.include_router(chatbot.router, prefix="/chat")
app.include_router(teams.router, prefix="/teams")
app.include_router(projects.router, prefix="/projects")

# --- Root Endpoint ---
@app.get("/")
def root():
    return {"status": "ok", "service": "WorkExperio Backend"}

