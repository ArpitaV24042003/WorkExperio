# import os
# import sys
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy import text
# from .database import engine,Base
# from app import models

# # --- Debugging ---
# # Print the database URL when the application starts
# print("="*50)
# print(f"DATABASE URL AT RUNTIME: {os.getenv('DATABASE_URL')}")
# print("="*50)

# # --- Router Imports ---
# # This assumes your project structure is correct
# from app.routers import (
#     mongo_routes,
#     projects,
#     users,
#     resumes,
#     chatbot,
#     teams,
# )

# # --- FastAPI App Initialization (Happens Only ONCE) ---
# app = FastAPI(title="WorkExperio API")

# # --- Middleware ---
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, restrict this to your frontend URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- Diagnostic Endpoint ---
# @app.get("/db-check")
# def check_db_tables():
#     try:
#         with engine.connect() as connection:
#             # Query to check if the 'users' table exists
#             query = text("""
#                 SELECT EXISTS (
#                     SELECT FROM information_schema.tables 
#                     WHERE table_schema = 'public' 
#                     AND table_name = 'users'
#                 );
#             """)
#             result = connection.execute(query).scalar()
#             return {"message": "Database check successful", "users_table_exists": result}
#     except Exception as e:
#         # Return the actual database error if the connection fails
#         return {"error": "Failed to connect or query database", "details": str(e)}

# # --- Register Routers ---
# app.include_router(mongo_routes.router, prefix="/mongo")
# app.include_router(users.router, prefix="/users")
# app.include_router(resumes.router, prefix="/resumes")
# app.include_router(chatbot.router, prefix="/chat")
# app.include_router(teams.router, prefix="/teams")
# app.include_router(projects.router, prefix="/projects")

# # --- Root Endpoint ---
# @app.get("/")
# def root():
#     return {"status": "ok", "service": "WorkExperio Backend"}

# print("Creating database tables if not exist...")
# Base.metadata.create_all(bind=engine)

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine, Base
from app import models

# Import Routers
from app.routers import (
    users,
    projects,
    teams,
    resumes,
    chatbot,
    mongo_routes,
)

# --- Print DATABASE_URL for debugging (visible in Render logs) ---
print("=" * 60)
print(f"DATABASE_URL at runtime: {os.getenv('DATABASE_URL')}")
print("=" * 60)

# --- FastAPI App Initialization ---
app = FastAPI(title="WorkExperio Backend API")

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Create Database Tables (only if not already created) ---
try:
    print("🔄 Creating database tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables verified or created successfully.")
except Exception as e:
    print("❌ Error creating tables:", e)

# --- Diagnostic Endpoint (for Render DB verification) ---
@app.get("/db-check")
def check_db_connection():
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
            return {
                "message": "Database connected successfully ✅",
                "users_table_exists": result
            }
    except Exception as e:
        return {
            "error": "Database connection failed ❌",
            "details": str(e)
        }

# --- Register All Routers ---
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(teams.router, prefix="/teams", tags=["Teams"])
app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(mongo_routes.router, prefix="/mongo", tags=["MongoDB"])

# --- Root Endpoint ---
@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "WorkExperio Backend Running 🚀",
        "database_url": os.getenv("DATABASE_URL", "Not Found")
    }
