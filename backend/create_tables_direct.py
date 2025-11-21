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
DATABASE_URL = "postgresql://workexperio_sopi_user:iF5kjz3zyGYDqj8f1Cxer4Bsa4ciJZaK@dpg-d4ddu96mcj7s73dvtml0-a.oregon-postgres.render.com/workexperio_sopi?sslmode=require"

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



