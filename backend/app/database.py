# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PostgreSQL connection string from .env
DATABASE_URL =os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory (used in routes)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models (used in models.py)
Base = declarative_base()

# Dependency for FastAPI routes (used with Depends)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
