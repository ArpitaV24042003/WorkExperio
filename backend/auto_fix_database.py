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
    
    # Show actual password (for debugging - user can see what's being used)
    if parsed.password:
        print(f"\n🔍 Password being used (first 4 chars): {parsed.password[:4]}***")
        print(f"🔍 Password length: {len(parsed.password)} characters")
    
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
        print("\n🔍 This means the password in DATABASE_URL doesn't match PostgreSQL")
        print("\n📋 Steps to fix:")
        print("1. Go to Render Dashboard → PostgreSQL service (workexperio-database)")
        print("2. Click 'Info' tab")
        print("3. Find 'Password' field")
        print("4. Click eye icon 👁️ to reveal the CURRENT password")
        print("5. Copy it EXACTLY (no spaces, no typos)")
        print("6. Go to Backend service → Environment tab")
        print("7. Edit DATABASE_URL")
        print("8. Find the password part (between : and @)")
        print("9. Replace it with the password from step 4")
        print("10. If password has special characters, they might need URL encoding")
        print("11. Save and redeploy")
        
        # Show connection string structure
        if parsed.username and parsed.hostname and parsed.path:
            print("\n💡 Connection string structure:")
            print(f"   postgresql://{parsed.username}:<PASSWORD>@{parsed.hostname}:{parsed.port or 5432}{parsed.path}?sslmode=require")
            print("\n   Replace <PASSWORD> with the EXACT password from Render dashboard")
            
            # Check if password might need encoding
            if parsed.password:
                from urllib.parse import quote_plus, unquote
                if parsed.password != unquote(parsed.password):
                    print(f"\n⚠️  Password appears to be URL-encoded")
                    print(f"   Decoded: {unquote(parsed.password)}")
                # Check for special characters
                special_chars = ['@', '#', '%', '/', ':', '?', '&', '=']
                has_special = any(char in parsed.password for char in special_chars)
                if has_special:
                    print(f"\n⚠️  Password contains special characters that might need encoding")
                    encoded = quote_plus(parsed.password)
                    print(f"   URL-encoded version: {encoded}")
                    print(f"   Try using the URL-encoded version in connection string")
    
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

