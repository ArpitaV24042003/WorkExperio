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
	"""
	if raw_url.startswith("postgres://"):
		raw_url = raw_url.replace("postgres://", "postgresql://", 1)
	try:
		url = make_url(raw_url)
	except ArgumentError:
		# If SQLAlchemy can't parse it, just return the raw value
		return raw_url

	if url.drivername in {"postgres", "postgresql"}:
		url = url.set(drivername="postgresql+psycopg")
	return str(url)


# Default to a persistent on-disk SQLite database for local development.
# This avoids in-memory databases that lose all data on restart.
DATABASE_URL = _normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./dev.db"))

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


