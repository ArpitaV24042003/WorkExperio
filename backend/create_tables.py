"""
Create all database tables directly
"""
import os
from app.db import Base, engine
from app import models  # Import all models

# Set your database URL here or use environment variable
# Add ?sslmode=require for Render PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://workexperio_sopi_user:iF5kjz3zyGYDqj8f1Cxer4Bsa4ciJZaK@dpg-d4ddu96mcj7s73dvtml0-a.oregon-postgres.render.com/workexperio_sopi?sslmode=require"
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

