"""
Test database connection with the provided password
"""
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text

# Database connection details - UPDATE THESE WITH YOUR NEW DATABASE
DB_USER = "workexperiodb_user"
DB_PASSWORD = "q9fWCuAxAdHrrWFNJzAqpsWotLgq8048"  # Get current password from Render dashboard
DB_HOST = "dpg-d4gqmp75r7bs73bem4u0-a.oregon-postgres.render.com"
DB_PORT = "5432"
DB_NAME = "workexperiodb"

# URL encode the password (in case it has special characters)
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)

# Construct connection string
DATABASE_URL = f"postgresql://{DB_USER}:{ENCODED_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

print("=" * 60)
print("Testing Database Connection")
print("=" * 60)
print(f"\nConnection String (password masked):")
print(f"postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require")
print(f"\nFull Connection String:")
print(DATABASE_URL)
print("\n" + "=" * 60)

# Test connection
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.scalar()
        print("✅ Connection SUCCESSFUL!")
        print(f"\nPostgreSQL Version: {version}")
        
        # Test query
        result = conn.execute(text("SELECT current_database();"))
        db_name = result.scalar()
        print(f"Connected to database: {db_name}")
        
        print("\n" + "=" * 60)
        print("✅ This connection string works!")
        print("Copy the DATABASE_URL above and use it in Render environment variables")
        print("=" * 60)
        
except Exception as e:
    print("❌ Connection FAILED!")
    print(f"\nError: {str(e)}")
    print("\n" + "=" * 60)
    print("Possible issues:")
    print("1. Password is incorrect")
    print("2. Database host/port is wrong")
    print("3. Database doesn't exist")
    print("4. Network connectivity issue")
    print("\nTry:")
    print("1. Get 'Internal Database URL' from Render PostgreSQL service")
    print("2. Use that connection string directly (it has the correct password)")
    print("=" * 60)

