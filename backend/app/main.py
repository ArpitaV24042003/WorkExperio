# app/main.py
import os
import sys
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import text

# ensure the app package dir is on sys.path (you already did this)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
import app.models  # ensure models are registered with SQLAlchemy metadata
from app.routers import auth as auth_router, ai as ai_router, users, resumes, mongo_routes, chatbot, teams, projects

# --- Debugging: Print database URL at runtime for logs ---
print("=" * 60)
print(f"DATABASE URL AT RUNTIME: {os.getenv('DATABASE_URL')}")
print("=" * 60)

# --- Initialize FastAPI App ---
app = FastAPI(
    title="WorkExperio API",
    version="1.0.0",
    description="Backend for WorkExperio project",
    servers=[
        {"url": os.getenv("BACKEND_BASE_URL", "https://workexperio.onrender.com"), "description": "Backend"},
        {"url": "http://127.0.0.1:8000", "description": "Local (Development)"},
    ],
)

# --- Session / CORS configuration (read from env for production) ---
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-me")
# Control whether SessionMiddleware sets https_only=True (recommended in production)
SESSION_HTTPS_ONLY = os.getenv("SESSION_HTTPS_ONLY", "true").lower() in ("1", "true", "yes")

# Allowed origins: read comma-separated list from env or fallback to defaults
_allowed = os.getenv(
    "ALLOWED_ORIGINS",
    ",".join(
        [
            "http://localhost:5173",
            "http://localhost:3000",
            "https://workexperio.onrender.com",
            "https://workexperio-1.onrender.com",
            "https://workexperio-2.onrender.com",
            "https://workexperio-3.onrender.com",
            "https://workexperio-4.onrender.com"
        ]
    ),
)
ALLOWED_ORIGINS = [o.strip() for o in _allowed.split(",") if o.strip()]

# SessionMiddleware: required by authlib/starlette OAuth flows (saves state)
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="session",
    max_age=14 * 24 * 60 * 60,  # 14 days
    same_site="lax",
    https_only=SESSION_HTTPS_ONLY,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(ai_router.router, prefix="/ai", tags=["AI"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
app.include_router(mongo_routes.router, prefix="/mongo", tags=["MongoDB"])
app.include_router(chatbot.router, prefix="/chat", tags=["Chat"])
app.include_router(teams.router, prefix="/teams", tags=["Teams"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])

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
            query = text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """
            )
            result = connection.execute(query).scalar()
            return {"message": "Database connection successful", "users_table_exists": bool(result)}
    except Exception as e:
        return {"error": "Failed to connect or query database", "details": str(e)}

# --- Create tables if they don’t exist ---
print("Creating database tables (if not exist)...")
Base.metadata.create_all(bind=engine)
print("✅ Database setup complete.")

# --- Run with uvicorn if executed directly ---
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))  # Render assigns port dynamically
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
