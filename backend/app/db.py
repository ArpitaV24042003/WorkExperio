from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os


def _normalize_database_url(raw_url: str) -> str:
	"""
	Normalize DATABASE_URL for different environments.

	- Upgrade legacy postgres:// URLs
	- Ensure psycopg driver for PostgreSQL
	- Preserve query parameters (like ?sslmode=require)
	- Preserve password EXACTLY as provided (don't let make_url modify it)
	"""
	if raw_url.startswith("postgres://"):
		raw_url = raw_url.replace("postgres://", "postgresql://", 1)
	
	# For PostgreSQL, preserve password exactly to avoid make_url() modifying it
	if raw_url.startswith("postgresql://"):
		# Extract components manually to preserve password exactly
		from urllib.parse import urlparse, urlunparse
		
		# Parse to get components
		parsed = urlparse(raw_url)
		
		# Preserve password exactly as-is (don't let make_url touch it)
		# Only change the scheme to use psycopg driver
		if parsed.password is not None:
			# Reconstruct with psycopg driver but keep password unchanged
			# Format: postgresql+psycopg://user:password@host:port/db?params
			new_scheme = "postgresql+psycopg"
			netloc = f"{parsed.username}:{parsed.password}@{parsed.hostname}"
			if parsed.port:
				netloc += f":{parsed.port}"
			
			new_parsed = parsed._replace(scheme=new_scheme, netloc=netloc)
			result = urlunparse(new_parsed)
			return result
	
	# For non-PostgreSQL or if parsing fails, use original logic
	query_params = ""
	if "?" in raw_url:
		base_url, query_params = raw_url.split("?", 1)
		query_params = "?" + query_params
	else:
		base_url = raw_url
	
	try:
		url = make_url(base_url)
	except ArgumentError:
		# If SQLAlchemy can't parse it, just return the raw value
		return raw_url

	if url.drivername in {"postgres", "postgresql"}:
		url = url.set(drivername="postgresql+psycopg")
	
	# Reconstruct URL with query parameters preserved
	result = str(url)
	if query_params and query_params not in result:
		result += query_params
	
	return result


# Default to a persistent on-disk SQLite database for local development.
# This avoids in-memory databases that lose all data on restart.
# Use absolute path to ensure persistence across directory changes
_default_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dev.db")
if not os.path.isabs(_default_db_path):
	_default_db_path = os.path.abspath(_default_db_path)

# Get raw DATABASE_URL from environment
_raw_database_url = os.getenv("DATABASE_URL", f"sqlite:///{_default_db_path}")

# Log the raw URL for debugging (password masked)
if _raw_database_url.startswith("postgresql"):
	import re
	_masked_url = re.sub(r"(postgresql://[^:]+:)([^@]+)(@)", r"\1***\3", _raw_database_url)
	import logging
	logger = logging.getLogger(__name__)
	logger.info(f"Raw DATABASE_URL (password masked): {_masked_url}")
	
	# Check if connection string is complete
	if "?sslmode=require" not in _raw_database_url:
		logger.warning("⚠️  DATABASE_URL missing ?sslmode=require - connection may fail!")
	if ":5432" not in _raw_database_url and ".oregon-postgres.render.com" not in _raw_database_url:
		logger.warning("⚠️  DATABASE_URL may be incomplete - missing full hostname or port!")

DATABASE_URL = _normalize_database_url(_raw_database_url)

# SQLite parameters
if DATABASE_URL.startswith("sqlite"):
	engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
	# PostgreSQL connection pool settings to prevent timeouts
	engine = create_engine(
		DATABASE_URL,
		pool_pre_ping=True,  # Verify connections before using
		pool_size=5,  # Number of connections to maintain
		max_overflow=10,  # Additional connections beyond pool_size
		pool_recycle=3600,  # Recycle connections after 1 hour
		connect_args={
			"connect_timeout": 10,  # Connection timeout in seconds
			"application_name": "workexperio_backend",
		} if "postgresql" in DATABASE_URL else {},
	)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
	pass


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def create_all_tables():
	"""
	Import all models and create tables if they do not exist.

	This is safe for SQLite and Postgres and is used on startup as a
	fallback in addition to Alembic migrations.
	"""
	# Local import to avoid circular
	from . import models  # noqa: F401
	Base.metadata.create_all(bind=engine)


