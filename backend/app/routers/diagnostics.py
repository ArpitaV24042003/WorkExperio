from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
import re

from ..db import get_db, engine, DATABASE_URL
from ..models import User, Project, Task

router = APIRouter()


@router.get("/diagnostics/database")
def database_diagnostics(db: Session = Depends(get_db)):
	"""
	Diagnostic endpoint to check database configuration and data persistence.
	This helps identify if the database is properly configured for persistence.
	"""
	import re
	
	raw_database_url = os.getenv("DATABASE_URL", "")
	
	# Mask password in URL for display (security)
	def mask_password(url_str):
		if not url_str:
			return "NOT SET"
		# Replace password with *** for display
		pattern = r"(postgresql://[^:]+:)([^@]+)(@)"
		masked = re.sub(pattern, r"\1***\3", url_str)
		return masked[:100] + "..." if len(masked) > 100 else masked
	
	diagnostics = {
		"database_url_set": bool(raw_database_url),
		"database_url_preview": mask_password(raw_database_url),
		"database_type": "unknown",
		"is_persistent": False,
		"warning": None,
		"user_count": 0,
		"project_count": 0,
		"task_count": 0,
		"connection_test": "unknown",
		"connection_error_details": None,
	}
	
	# Check database type
	if DATABASE_URL.startswith("sqlite"):
		diagnostics["database_type"] = "SQLite"
		diagnostics["is_persistent"] = False
		diagnostics["warning"] = (
			"⚠️ CRITICAL: Using SQLite database. "
			"SQLite on Render uses ephemeral storage - ALL DATA WILL BE LOST on restart/deploy! "
			"You MUST set DATABASE_URL to a PostgreSQL connection string in Render environment variables."
		)
	elif DATABASE_URL.startswith("postgresql"):
		diagnostics["database_type"] = "PostgreSQL"
		diagnostics["is_persistent"] = True
		
		# Extract connection details for troubleshooting
		try:
			from urllib.parse import urlparse
			parsed = urlparse(DATABASE_URL)
			diagnostics["postgresql_host"] = parsed.hostname
			diagnostics["postgresql_port"] = parsed.port
			diagnostics["postgresql_database"] = parsed.path.lstrip("/")
			diagnostics["postgresql_user"] = parsed.username
		except Exception:
			pass
		
		diagnostics["warning"] = None
	else:
		diagnostics["database_type"] = "Unknown"
		diagnostics["warning"] = f"Unknown database type: {DATABASE_URL[:50]}"
	
	# Test connection
	try:
		with engine.connect() as conn:
			conn.execute(text("SELECT 1"))
			diagnostics["connection_test"] = "✅ Connected"
	except Exception as e:
		error_msg = str(e)
		diagnostics["connection_test"] = f"❌ Error: {error_msg[:200]}"
		diagnostics["connection_error_details"] = error_msg
		
		# Provide specific guidance based on error type
		if "password authentication failed" in error_msg.lower():
			diagnostics["fix_instructions"] = (
				"Password authentication failed. Steps to fix:\n"
				"1. Go to Render Dashboard → PostgreSQL service → Info tab\n"
				"2. Copy the 'Internal Database URL' (this has the CURRENT password)\n"
				"3. Go to Backend service → Environment tab\n"
				"4. Update DATABASE_URL with the NEW connection string\n"
				"5. Make sure it includes ?sslmode=require at the end\n"
				"6. Save and wait for redeploy"
			)
		elif "connection" in error_msg.lower() and "failed" in error_msg.lower():
			diagnostics["fix_instructions"] = (
				"Connection failed. Check:\n"
				"1. PostgreSQL service is running in Render\n"
				"2. DATABASE_URL has correct host and port\n"
				"3. Network connectivity (use Internal Database URL, not External)"
			)
	
	# Count existing data
	try:
		diagnostics["user_count"] = db.query(User).count()
		diagnostics["project_count"] = db.query(Project).count()
		diagnostics["task_count"] = db.query(Task).count()
	except Exception as e:
		diagnostics["data_count_error"] = str(e)[:200]
	
	return diagnostics

