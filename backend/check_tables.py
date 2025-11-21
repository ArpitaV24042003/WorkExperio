"""
Check database tables and schemas
"""
import os
from app.db import engine
from sqlalchemy import inspect, text

# Set database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://workexperio_sopi_user:iF5kjz3zyGYDqj8f1Cxer4Bsa4ciJZaK@dpg-d4ddu96mcj7s73dvtml0-a.oregon-postgres.render.com/workexperio_sopi"
)

if __name__ == "__main__":
    print("🔍 Checking database...")
    
    inspector = inspect(engine)
    
    # Check current database
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database();"))
        db_name = result.scalar()
        print(f"📊 Current database: {db_name}")
        
        result = conn.execute(text("SELECT current_schema();"))
        schema_name = result.scalar()
        print(f"📁 Current schema: {schema_name}")
    
    # List all schemas
    print("\n📂 All schemas:")
    schemas = inspector.get_schema_names()
    for schema in schemas:
        print(f"   • {schema}")
    
    # Check tables in public schema
    print("\n📋 Tables in 'public' schema:")
    tables = inspector.get_table_names(schema='public')
    if tables:
        for table in sorted(tables):
            print(f"   ✅ {table}")
    else:
        print("   ❌ No tables found in 'public' schema")
    
    # Check tables in all schemas
    print("\n📋 Tables in all schemas:")
    found_any = False
    for schema in schemas:
        tables = inspector.get_table_names(schema=schema)
        if tables:
            found_any = True
            print(f"\n   Schema: {schema}")
            for table in sorted(tables):
                print(f"      • {table}")
    
    if not found_any:
        print("   ❌ No tables found in any schema!")
        print("\n🔄 Creating tables now...")
        from app.db import Base
        from app import models
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created! Run this script again to verify.")



