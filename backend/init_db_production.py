"""
Production Database Initialization Script
Creates all tables and verifies database connection
"""
import os
import sys
from sqlalchemy import text, inspect

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import engine, Base, SessionLocal
from app import models  # Import to register all models

def init_database():
    """Initialize database tables"""
    print("🔧 Initializing WorkExperio Database...")
    print(f"Database URL: {engine.url}")
    print()
    
    # Create all tables
    try:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    # Verify tables
    print()
    print("Verifying tables...")
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    
    expected_tables = {
        "users", "resumes", "educations", "experiences", "skills",
        "projects", "teams", "team_members", "project_waitlists",
        "chat_messages", "user_stats", "model_predictions"
    }
    
    missing = expected_tables - existing_tables
    if missing:
        print(f"❌ Missing tables: {missing}")
        return False
    
    print(f"✅ All {len(expected_tables)} tables exist")
    
    # Test connection
    print()
    print("Testing database connection...")
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    finally:
        db.close()
    
    print()
    print("✅ Database initialization complete!")
    return True

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)

