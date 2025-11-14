from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState
import time

from .routers import auth, resumes, users, projects, teams, chat, ai, xp, metrics, admin
from .db import create_all_tables
from .metrics_store import metrics_store


def create_app() -> FastAPI:
	"""
	Create and configure the FastAPI application instance.
	"""
	app = FastAPI(title="WorkExperio API", version="0.1.0")

	# CORS
	origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
	app.add_middleware(
		CORSMiddleware,
		allow_origins=origins,
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	# Mount routers
	app.include_router(auth.router, prefix="/auth", tags=["auth"])
	app.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
	app.include_router(users.router, prefix="/users", tags=["users"])
	app.include_router(projects.router, prefix="/projects", tags=["projects"])
	app.include_router(teams.router, tags=["teams"])
	app.include_router(chat.router, tags=["chat"])
	app.include_router(ai.router, prefix="/ai", tags=["ai"])
	app.include_router(xp.router, prefix="/users", tags=["xp"])
	app.include_router(metrics.router, tags=["metrics"])
	app.include_router(admin.router, prefix="/admin", tags=["admin"])

	# Simple middleware for request metrics (duration)
	@app.middleware("http")
	async def add_timing_header(request, call_next):
		start_time = time.perf_counter()
		response = await call_next(request)
		duration_ms = int((time.perf_counter() - start_time) * 1000)
		response.headers["X-Process-Time-ms"] = str(duration_ms)
		metrics_store.record_request(duration_ms)
		return response

	@app.on_event("startup")
	def on_startup():
		create_all_tables()

	return app


app = create_app()

# app/main.py
import os
import sys
import traceback
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import text

# ensure the app package dir is on sys.path (you already did this)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
import app.models  # ensure models are registered with SQLAlchemy metadata

# existing routers from your app package
from app.routers import auth as auth_router
from app.routers import users, resumes, mongo_routes, chatbot, teams, projects
# Note: you already had ai as ai_router included earlier; we'll still include if present.
try:
    from app.routers import ai as ai_router
except Exception:
    ai_router = None

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
            "https://workexperio-4.onrender.com",
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

# --- Include core Routers (your existing app routers) ---
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
if ai_router:
    try:
        app.include_router(ai_router.router, prefix="/ai", tags=["AI"])
    except Exception:
        print("Could not include app.routers.ai router (it may be missing).")

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
app.include_router(mongo_routes.router, prefix="/mongo", tags=["MongoDB"])
app.include_router(chatbot.router, prefix="/chat", tags=["Chat"])
app.include_router(teams.router, prefix="/teams", tags=["Teams"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])

# --- BEST-EFFORT: include ai_service modules under /ai if present ---
# This helps when ai_service is a sibling package and its modules expose functions
# or APIRouters. We try two patterns:
# 1) module exposes an APIRouter named `router`: include it directly
# 2) module exposes functions we can call — create small wrapper endpoints

def _try_include_external_router(module_path: str, prefix: str, tag: str):
    """
    Try to import module_path and include its `router` attribute under `prefix`.
    Returns True on success, False otherwise.
    """
    try:
        mod = __import__(module_path, fromlist=["router"])
        router_obj = getattr(mod, "router", None)
        if router_obj:
            app.include_router(router_obj, prefix=prefix, tags=[tag])
            print(f"Included external router {module_path} under prefix {prefix}")
            return True
        else:
            print(f"Module {module_path} found but has no 'router' attribute")
            return False
    except ModuleNotFoundError:
        print(f"Module {module_path} not found (ModuleNotFoundError)")
        return False
    except Exception:
        print(f"Failed to import {module_path}:")
        traceback.print_exc()
        return False

# Try to mount AI modules under /ai/team and /ai (best-effort)
_ai_base = "ai_service.ai_model"
# team_ps_selection router or function
if not _try_include_external_router(_ai_base + ".team_ps_selection", "/ai/team", "AI-Team"):
    # fallback wrapper - try to import functions and create endpoints if available
    try:
        team_ps_mod = __import__(_ai_base + ".team_ps_selection", fromlist=["select_ps"])
        select_fn = getattr(team_ps_mod, "select_ps", None) or getattr(team_ps_mod, "run_selection", None)
        if select_fn:
            wrapper = APIRouter(prefix="/ai/team", tags=["AI-Team"])

            # Support both sync and async select functions
            async def _call_select(payload: dict):
                res = select_fn(payload)
                if hasattr(res, "__await__"):  # coroutine
                    return await res
                return res

            @wrapper.post("/ps-selection")
            async def ps_selection_endpoint(payload: dict):
                try:
                    return await _call_select(payload)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))

            app.include_router(wrapper)
            print("Mounted fallback wrapper for ai_service.ai_model.team_ps_selection at /ai/team/ps-selection")
        else:
            print("ai_service.ai_model.team_ps_selection exists but no select function found.")
    except ModuleNotFoundError:
        print("ai_service.ai_model.team_ps_selection not present (skip).")
    except Exception:
        traceback.print_exc()

# try resume parser module (if it exposes router)
_try_include_external_router(_ai_base + ".resume_parsing", "/ai/resume", "AI-Resume")

# try other ai modules e.g., team_formation, make_prediction
_try_include_external_router(_ai_base + ".team_formation", "/ai/team-formation", "AI-Team-Formation")
_try_include_external_router(_ai_base + ".make_prediction", "/ai/predict", "AI-Prediction")

# try to include chat_interface.router if available (prefix /chat-interface)
try:
    chat_mod = __import__("chat_interface", fromlist=["router"])
    chat_router = getattr(chat_mod, "router", None)
    if chat_router:
        app.include_router(chat_router, prefix="/chat", tags=["ChatInterface"])
        print("Included chat_interface.router under /chat")
    else:
        print("chat_interface module found but no 'router' attribute")
except ModuleNotFoundError:
    print("chat_interface module not found; skipping chat inclusion")

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
