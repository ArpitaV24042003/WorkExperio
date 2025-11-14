from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os


def _normalize_database_url(raw_url: str) -> str:
	if raw_url.startswith("postgres://"):
		raw_url = raw_url.replace("postgres://", "postgresql://", 1)
	try:
		url = make_url(raw_url)
	except ArgumentError:
		return raw_url

	if url.drivername in {"postgres", "postgresql"}:
		url = url.set(drivername="postgresql+psycopg")
	return str(url)


DATABASE_URL = _normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./backend/app.db"))

# SQLite parameters
if DATABASE_URL.startswith("sqlite"):
	engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
	engine = create_engine(DATABASE_URL, pool_pre_ping=True)

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
	# Local import to avoid circular
	from . import models  # noqa: F401
	Base.metadata.create_all(bind=engine)


