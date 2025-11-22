"""
Test database connection directly - Run this in Render Shell
"""
import os
import sys
from urllib.parse import urlparse, quote_plus
from sqlalchemy import create_engine, text

def test_connection_string(connection_string):
    """Test a connection string"""
    print(f"\n{'='*60}")
    print("Testing Connection String:")
    print(f"{'='*60}")
    
    # Mask password for display
    parsed = urlparse(connection_string)
    masked = f"{parsed.scheme}://{parsed.username}:***@{parsed.hostname}:{parsed.port}{parsed.path}"
    print(f"Connection: {masked}")
    print(f"Host: {parsed.hostname}")
    print(f"Port: {parsed.port}")
    print(f"Database: {parsed.path.lstrip('/')}")
    print(f"User: {parsed.username}")
    print(f"SSL Mode: {parsed.query}")
    
    try:
        engine = create_engine(connection_string, pool_pre_ping=True, connect_args={
            "connect_timeout": 10
        })
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"\n✅ Connection SUCCESSFUL!")
            print(f"PostgreSQL Version: {version}")
            
            # Test database name
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.scalar()
            print(f"Connected to database: {db_name}")
            
            # Test user
            result = conn.execute(text("SELECT current_user;"))
            user = result.scalar()
            print(f"Connected as user: {user}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Connection FAILED!")
        print(f"Error: {str(e)}")
        
        # Provide specific guidance
        error_str = str(e).lower()
        if "password authentication failed" in error_str:
            print("\n🔍 Issue: Password is WRONG")
            print("   - The password in the connection string doesn't match the database")
            print("   - Try: Get a fresh 'Internal Database URL' from Render")
            print("   - Or: Check if password was changed in Render")
        elif "connection" in error_str and "refused" in error_str:
            print("\n🔍 Issue: Cannot reach database server")
            print("   - Check if database service is running")
            print("   - Check if database is paused")
            print("   - Verify network connectivity")
        elif "does not exist" in error_str:
            print("\n🔍 Issue: Database doesn't exist")
            print("   - Check database name in connection string")
        else:
            print(f"\n🔍 Error type: {type(e).__name__}")
        
        return False

if __name__ == "__main__":
    print("="*60)
    print("Database Connection Tester")
    print("="*60)
    
    # Get DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("\n❌ DATABASE_URL environment variable is NOT SET!")
        print("\nTo test a connection string manually, run:")
        print("  DATABASE_URL='your_connection_string' python test_db_connection.py")
        sys.exit(1)
    
    print(f"\nDATABASE_URL from environment:")
    parsed = urlparse(database_url)
    print(f"  Host: {parsed.hostname}")
    print(f"  Port: {parsed.port}")
    print(f"  Database: {parsed.path.lstrip('/')}")
    print(f"  User: {parsed.username}")
    
    # Test the connection
    success = test_connection_string(database_url)
    
    if not success:
        print("\n" + "="*60)
        print("Troubleshooting Steps:")
        print("="*60)
        print("1. Go to Render Dashboard → PostgreSQL service → Info tab")
        print("2. Copy 'Internal Database URL' (click copy icon)")
        print("3. Verify it includes: hostname, port, database, ?sslmode=require")
        print("4. Check if database service is running (not paused)")
        print("5. Try resetting password in Render (if available)")
        print("6. Check if you're using the correct database instance")
        print("="*60)
        sys.exit(1)
    else:
        print("\n" + "="*60)
        print("✅ Connection test PASSED!")
        print("="*60)
        sys.exit(0)

