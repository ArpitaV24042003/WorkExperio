"""
Create all database tables directly
"""
import os
from app.db import Base, engine
from app import models  # Import all models

# Set your database URL here or use environment variable
# Add ?sslmode=require for Render PostgreSQL
# IMPORTANT: Never hardcode passwords! Always use environment variable.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Set it in Render environment variables with your PostgreSQL connection string."
    )

if __name__ == "__main__":
    print("🔄 Creating all database tables...")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        print("\n📊 Tables created:")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        for table in sorted(tables):
            print(f"   • {table}")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

