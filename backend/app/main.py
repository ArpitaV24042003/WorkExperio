from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState
from datetime import datetime
import time

from .routers import auth, resumes, users, projects, teams, chat, ai, xp, metrics, admin
from .db import create_all_tables
from .metrics_store import metrics_store


def create_app() -> FastAPI:
	"""
	Create and configure the FastAPI application instance.
	"""
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
		# Try to create tables, but don't fail if database is not available
		try:
			create_all_tables()
		except Exception as e:
			import logging
			logger = logging.getLogger(__name__)
			logger.warning(f"Could not create database tables on startup: {e}")
			logger.warning("Server will start, but database operations may fail until DATABASE_URL is configured correctly.")

	return app


app = create_app()


if __name__ == "__main__":
	import uvicorn
	import os
	port = int(os.getenv("PORT", 8000))
	uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=os.getenv("ENV") == "development")
