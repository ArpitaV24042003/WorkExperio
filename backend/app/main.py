from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState
from datetime import datetime
import time

from .routers import (
	auth,
	resumes,
	users,
	projects,
	teams,
	chat,
	ai,
	xp,
	metrics,
	admin,
	ai_team_formation,
	files,
	domains,
	projects_dashboard,
	diagnostics,
)
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
		from .db import engine, DATABASE_URL
		from sqlalchemy import text
		
		db_status = "unknown"
		database_url = os.getenv("DATABASE_URL", "")
		db_type = "unknown"
		table_count = 0
		
		try:
			# Determine database type
			if DATABASE_URL.startswith("sqlite"):
				db_type = "SQLite (⚠️ Ephemeral - data will be lost on restart!)"
			elif DATABASE_URL.startswith("postgresql"):
				db_type = "PostgreSQL (✅ Persistent)"
			else:
				db_type = f"Unknown: {DATABASE_URL[:50]}"
			
			# Test database connection
			with engine.connect() as conn:
				conn.execute(text("SELECT 1"))
				db_status = "connected"
				
				# Try to count tables to verify persistence
				try:
					if DATABASE_URL.startswith("postgresql"):
						result = conn.execute(text("""
							SELECT COUNT(*) FROM information_schema.tables 
							WHERE table_schema = 'public'
						"""))
						table_count = result.scalar() or 0
					elif DATABASE_URL.startswith("sqlite"):
						result = conn.execute(text("""
							SELECT COUNT(*) FROM sqlite_master 
							WHERE type='table' AND name NOT LIKE 'sqlite_%'
						"""))
						table_count = result.scalar() or 0
				except Exception:
					table_count = -1
		except Exception as e:
			db_status = f"error: {str(e)[:100]}"
		
		return {
			"status": "healthy" if db_status == "connected" else "degraded",
			"database": db_status,
			"database_type": db_type,
			"database_url_set": bool(database_url),
			"database_url_preview": database_url[:50] + "..." if len(database_url) > 50 else database_url if database_url else "NOT SET",
			"tables_found": table_count,
			"warning": "⚠️ Using SQLite - data will be lost on restart! Set DATABASE_URL to PostgreSQL." if DATABASE_URL.startswith("sqlite") else None,
			"timestamp": datetime.utcnow().isoformat()
		}

	# Mount routers
	app.include_router(auth.router, prefix="/auth", tags=["auth"])
	app.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
	app.include_router(users.router, prefix="/users", tags=["users"])
	app.include_router(projects.router, prefix="/projects", tags=["projects"])
	app.include_router(projects_dashboard.router, tags=["project-dashboard"])
	app.include_router(teams.router, prefix="/teams", tags=["teams"])
	app.include_router(chat.router, tags=["chat"])
	app.include_router(ai.router, prefix="/ai", tags=["ai"])
	app.include_router(ai_team_formation.router, prefix="/ai", tags=["ai"])
	app.include_router(xp.router, prefix="/users", tags=["xp"])
	app.include_router(metrics.router, tags=["metrics"])
	app.include_router(admin.router, prefix="/admin", tags=["admin"])
	app.include_router(files.router, prefix="/files", tags=["files"])
	app.include_router(domains.router, prefix="/domains", tags=["domains"])
	app.include_router(diagnostics.router, tags=["diagnostics"])
	app.include_router(diagnostics.router, tags=["diagnostics"])

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
		from .db import DATABASE_URL
		
		logger = logging.getLogger(__name__)
		logger.info("Starting WorkExperio API...")
		
		# Check database configuration
		database_url = os.getenv("DATABASE_URL", "")
		if not database_url:
			logger.error("❌ CRITICAL: DATABASE_URL environment variable is NOT SET!")
			logger.error("❌ The application will use SQLite, which is EPHEMERAL on Render!")
			logger.error("❌ ALL DATA WILL BE LOST on restart/deploy!")
			logger.error("❌ You MUST set DATABASE_URL in Render environment variables to a PostgreSQL connection string!")
		elif DATABASE_URL.startswith("sqlite"):
			logger.warning("⚠️  WARNING: Using SQLite database!")
			logger.warning("⚠️  SQLite on Render uses ephemeral storage - ALL DATA WILL BE LOST on restart/deploy!")
			logger.warning("⚠️  Set DATABASE_URL to a PostgreSQL connection string in Render environment variables!")
		elif DATABASE_URL.startswith("postgresql"):
			logger.info("✅ Using PostgreSQL database - data will persist!")
		else:
			logger.warning(f"⚠️  Unknown database type: {DATABASE_URL[:50]}")
		
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
