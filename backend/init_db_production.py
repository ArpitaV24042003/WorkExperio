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
    
    # Test connection first
    print("Testing database connection...")
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        db.close()
        print("✅ Database connection successful")
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️  Database connection failed: {error_msg[:200]}")
        
        # Provide specific guidance based on error
        if "password authentication failed" in error_msg.lower():
            print("\n🔍 Issue: Password authentication failed")
            print("📋 To fix:")
            print("   1. Go to Render Dashboard → PostgreSQL service → Info tab")
            print("   2. Find 'Password' field and click eye icon 👁️ to reveal it")
            print("   3. Copy the CURRENT password")
            print("   4. Go to Backend service → Environment tab")
            print("   5. Edit DATABASE_URL and replace the password part")
            print("   6. Format: postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE?sslmode=require")
            print("\n💡 Run 'python auto_fix_database.py' in Render Shell for automated diagnosis")
        elif "connection" in error_msg.lower() and "refused" in error_msg.lower():
            print("⚠️  Issue: Cannot reach database server")
            print("📋 Check if database service is running (not paused)")
        else:
            print("⚠️  This might be due to:")
            print("   1. DATABASE_URL environment variable not set correctly")
            print("   2. Database credentials are incorrect")
            print("   3. Database server is not accessible")
        
        print("⚠️  Skipping table creation. Please check your DATABASE_URL in Render environment variables.")
        return False
    
    # Create all tables
    try:
        print()
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
        "chat_messages", "user_stats", "model_predictions", "project_files",
        "ai_conversations"
    }
    
    missing = expected_tables - existing_tables
    if missing:
        print(f"❌ Missing tables: {missing}")
        return False
    
    print(f"✅ All {len(expected_tables)} tables exist")
    
    # Connection already tested above
    
    print()
    print("✅ Database initialization complete!")
    return True

if __name__ == "__main__":
    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("⚠️  DATABASE_URL environment variable not set")
        print("⚠️  Database initialization will be skipped")
        print("⚠️  Make sure DATABASE_URL is set in Render environment variables")
        print("⚠️  You can initialize the database manually after deployment using Render Shell")
        sys.exit(0)  # Don't fail the build, just skip DB init
    
    success = init_database()
    if not success:
        print()
        print("⚠️  Database initialization failed, but build will continue")
        print("⚠️  You can initialize the database manually after deployment:")
        print("   1. Go to Render Dashboard > Your Service > Shell")
        print("   2. Run: cd backend && python init_db_production.py")
        sys.exit(0)  # Don't fail the build, allow manual initialization
    sys.exit(0)

