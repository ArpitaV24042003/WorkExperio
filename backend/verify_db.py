"""
Database verification script - checks if all required tables exist
"""
from app.db import engine, SessionLocal
from sqlalchemy import inspect, text
from app import models  # Import to register models

def verify_tables():
    """Verify all required tables exist in the database"""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    
    # Expected tables from models
    expected_tables = {
        "users",
        "resumes",
        "educations",
        "experiences",
        "skills",
        "projects",
        "teams",
        "team_members",
        "project_waitlists",
        "chat_messages",
        "user_stats",
        "model_predictions"
    }
    
    print("🔍 Checking database tables...")
    print(f"Database URL: {engine.url}")
    print()
    
    missing_tables = expected_tables - existing_tables
    existing_expected = expected_tables & existing_tables
    
    if existing_expected:
        print(f"✅ Found {len(existing_expected)} expected tables:")
        for table in sorted(existing_expected):
            print(f"   ✓ {table}")
    
    if missing_tables:
        print(f"\n❌ Missing {len(missing_tables)} tables:")
        for table in sorted(missing_tables):
            print(f"   ✗ {table}")
        return False
    
    # Check for extra tables
    extra_tables = existing_tables - expected_tables
    if extra_tables:
        print(f"\n⚠️  Found {len(extra_tables)} extra tables (not in models):")
        for table in sorted(extra_tables):
            print(f"   ? {table}")
    
    # Verify table structure for key tables
    print("\n🔍 Verifying table structures...")
    db = SessionLocal()
    try:
        # Check users table columns
        users_columns = [col['name'] for col in inspector.get_columns('users')]
        required_user_columns = {'id', 'name', 'email', 'password_hash', 'created_at', 'profile_completed', 'xp_points', 'github_id', 'avatar_url', 'auth_provider'}
        missing_cols = required_user_columns - set(users_columns)
        if missing_cols:
            print(f"❌ Users table missing columns: {missing_cols}")
            return False
        else:
            print("✅ Users table structure is correct")
        
        # Test database connection
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        print("✅ Database connection successful")
        
    except Exception as e:
        print(f"❌ Database verification error: {e}")
        return False
    finally:
        db.close()
    
    print("\n✅ All database tables verified successfully!")
    return True

if __name__ == "__main__":
    success = verify_tables()
    exit(0 if success else 1)

