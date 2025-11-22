"""
Automated Database Connection Fix Script
Run this in Render Shell to automatically diagnose and fix database connection issues
"""
import os
import sys
from urllib.parse import urlparse, quote_plus
from sqlalchemy import create_engine, text

def test_connection(connection_string, description=""):
    """Test a connection string and return success status"""
    print(f"\n{'='*60}")
    if description:
        print(f"Testing: {description}")
    print(f"{'='*60}")
    
    try:
        engine = create_engine(connection_string, pool_pre_ping=True, connect_args={
            "connect_timeout": 10
        })
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ Connection SUCCESSFUL!")
            print(f"PostgreSQL Version: {version}")
            return True, connection_string
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Connection FAILED!")
        print(f"Error: {error_msg[:200]}")
        return False, error_msg

def auto_fix_database():
    """Automatically diagnose and attempt to fix database connection"""
    print("="*60)
    print("Automated Database Connection Fix")
    print("="*60)
    
    # Get current DATABASE_URL
    current_url = os.getenv("DATABASE_URL", "")
    
    if not current_url:
        print("\n❌ DATABASE_URL is not set!")
        print("\nTo fix:")
        print("1. Go to Render Dashboard → Backend service → Environment")
        print("2. Add DATABASE_URL with your PostgreSQL connection string")
        return False
    
    print(f"\n📋 Current DATABASE_URL (password masked):")
    parsed = urlparse(current_url)
    masked = f"{parsed.scheme}://{parsed.username}:***@{parsed.hostname}:{parsed.port}{parsed.path}"
    print(f"   {masked}")
    
    # Test current connection
    print("\n🔍 Testing current connection...")
    success, error = test_connection(current_url, "Current DATABASE_URL")
    
    if success:
        print("\n✅ Your current DATABASE_URL works! No fix needed.")
        return True
    
    # Analyze the error
    print("\n🔍 Analyzing error...")
    
    if "password authentication failed" in error.lower():
        print("\n❌ Issue: Password authentication failed")
        print("\n📋 To fix:")
        print("1. Go to Render Dashboard → PostgreSQL service → Info tab")
        print("2. Find 'Password' field and click eye icon to reveal it")
        print("3. Copy the password")
        print("4. Go to Backend service → Environment tab")
        print("5. Edit DATABASE_URL and replace the password")
        print("6. Make sure connection string format is:")
        print("   postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE?sslmode=require")
        
        # Try to construct a test connection string
        if parsed.username and parsed.hostname and parsed.path:
            print("\n💡 Suggested connection string format:")
            print(f"   postgresql://{parsed.username}:<PASSWORD_FROM_RENDER>@{parsed.hostname}:{parsed.port or 5432}{parsed.path}?sslmode=require")
            print("\n   Replace <PASSWORD_FROM_RENDER> with the actual password from Render dashboard")
    
    elif "connection" in error.lower() and ("refused" in error.lower() or "failed" in error.lower()):
        print("\n❌ Issue: Cannot connect to database server")
        print("\n📋 Check:")
        print("1. Database service is running (not paused)")
        print("2. Database region matches backend region")
        print("3. Using 'Internal Database URL' (not External)")
    
    elif "does not exist" in error.lower():
        print("\n❌ Issue: Database doesn't exist")
        print("\n📋 Check database name in connection string")
    
    else:
        print(f"\n❌ Unknown error: {error[:200]}")
    
    return False

if __name__ == "__main__":
    success = auto_fix_database()
    sys.exit(0 if success else 1)

