"""
Create all database tables directly - bypasses app imports
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Text, Boolean, Integer, Float, DateTime, ForeignKey
from datetime import datetime
import uuid

# Database URL with SSL
# IMPORTANT: Never hardcode passwords! Always use environment variable.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Set it in Render environment variables with your PostgreSQL connection string."
    )

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

class Base(DeclarativeBase):
    pass

if __name__ == "__main__":
    print("🔄 Creating all database tables directly...")
    
    # Import models to register them
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        # Import all models
        from app.models import Base as AppBase
        from app import models
        
        # Create all tables
        AppBase.metadata.create_all(bind=engine)
        
        print("✅ All tables created successfully!")
        
        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            
            print(f"\n📊 Found {len(tables)} tables:")
            for table in tables:
                print(f"   ✅ {table}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()



