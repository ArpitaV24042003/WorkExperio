from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState
from datetime import datetime
import time

from .routers import auth, resumes, users, projects, teams, chat, ai, xp, metrics, admin, ai_team_formation, files, domains
from .db import create_all_tables
from .metrics_store import metrics_store


def create_app() -> FastAPI:
	"""
	Create and configure the FastAPI application instance.
	"""
	import logging
	import sys
	
	# Configure logging for Render
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		handlers=[logging.StreamHandler(sys.stdout)]
	)
	
	app = FastAPI(title="WorkExperio API", version="0.1.0")

	# CORS - Read from environment or use defaults
	import os
	allow_origins_str = os.getenv("ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
	origins = [origin.strip() for origin in allow_origins_str.split(",") if origin.strip()]
	
	app.add_middleware(
		CORSMiddleware,
		allow_origins=origins,
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	# Root and health check endpoints
	@app.get("/")
	async def root():
		return {
			"message": "WorkExperio API",
			"version": "0.1.0",
			"status": "running",
			"docs": "/docs"
		}
	
	@app.get("/health")
	async def health_check():
		"""Health check endpoint that verifies database connection"""
		import os
		from .db import engine
		from sqlalchemy import text
		
		db_status = "unknown"
		database_url = os.getenv("DATABASE_URL", "")
		
		try:
			# Test database connection
			with engine.connect() as conn:
				conn.execute(text("SELECT 1"))
				db_status = "connected"
		except Exception as e:
			db_status = f"error: {str(e)[:100]}"
		
		return {
			"status": "healthy" if db_status == "connected" else "degraded",
			"database": db_status,
			"database_url_set": bool(database_url),
			"timestamp": datetime.utcnow().isoformat()
		}

	# Mount routers
	app.include_router(auth.router, prefix="/auth", tags=["auth"])
	app.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
	app.include_router(users.router, prefix="/users", tags=["users"])
	app.include_router(projects.router, prefix="/projects", tags=["projects"])
	app.include_router(teams.router, prefix="/teams", tags=["teams"])
	app.include_router(chat.router, tags=["chat"])
	app.include_router(ai.router, prefix="/ai", tags=["ai"])
	app.include_router(ai_team_formation.router, prefix="/ai", tags=["ai"])
	app.include_router(xp.router, prefix="/users", tags=["xp"])
	app.include_router(metrics.router, tags=["metrics"])
	app.include_router(admin.router, prefix="/admin", tags=["admin"])
	app.include_router(files.router, prefix="/files", tags=["files"])
	app.include_router(domains.router, prefix="/domains", tags=["domains"])

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
	async def on_startup():
		# Try to create tables, but don't fail if database is not available
		import logging
		import sys
		logger = logging.getLogger(__name__)
		logger.info("Starting WorkExperio API...")
		try:
			logger.info("Initializing database tables...")
			# For PostgreSQL on Render, tables should be created via migrations
			# But we also call create_all_tables as a fallback for new tables
			create_all_tables()
			logger.info("✅ Database tables initialized successfully")
		except Exception as e:
			logger.error(f"❌ Could not create database tables on startup: {e}")
			logger.warning("⚠️  Server will start, but database operations may fail until DATABASE_URL is configured correctly.")
			logger.warning("⚠️  Make sure to run migrations: alembic upgrade head")
			# Don't raise - allow server to start even if DB init fails
		logger.info("✅ WorkExperio API started successfully")

	return app


app = create_app()


if __name__ == "__main__":
	import uvicorn
	import os
	port = int(os.getenv("PORT", 8000))
	uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=os.getenv("ENV") == "development")
