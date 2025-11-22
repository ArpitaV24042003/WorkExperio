"""
Test script to show EXACT password being used vs what should be used
Run this in Render Shell to see if password is being modified
"""
import os
from urllib.parse import urlparse, unquote, quote_plus
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

def _normalize_database_url(raw_url: str) -> str:
    """Same function as in db.py"""
    if raw_url.startswith("postgres://"):
        raw_url = raw_url.replace("postgres://", "postgresql://", 1)
    
    query_params = ""
    if "?" in raw_url:
        base_url, query_params = raw_url.split("?", 1)
        query_params = "?" + query_params
    else:
        base_url = raw_url
    
    try:
        url = make_url(base_url)
    except ArgumentError:
        return raw_url

    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+psycopg")
    
    result = str(url)
    if query_params and query_params not in result:
        result += query_params
    
    return result

# Get DATABASE_URL from environment
raw_url = os.getenv("DATABASE_URL", "")
if not raw_url:
    print("❌ DATABASE_URL not set!")
    exit(1)

print("="*70)
print("PASSWORD DIAGNOSTIC - Checking if password is being modified")
print("="*70)

# Parse original URL
parsed_original = urlparse(raw_url)
original_password = parsed_original.password or ""

print(f"\n📋 ORIGINAL DATABASE_URL (from environment):")
print(f"   {raw_url[:50]}...")

print(f"\n🔍 ORIGINAL PASSWORD (from URL parse):")
print(f"   Raw: {original_password}")
print(f"   Length: {len(original_password)} characters")
if original_password:
    print(f"   First 4 chars: {original_password[:4]}")
    print(f"   Last 4 chars: {original_password[-4:]}")
    
    # Check if it's URL encoded
    decoded = unquote(original_password)
    if decoded != original_password:
        print(f"   ⚠️  URL-encoded! Decoded: {decoded}")
    else:
        print(f"   ✅ Not URL-encoded")

# Normalize (same as db.py does)
normalized_url = _normalize_database_url(raw_url)
parsed_normalized = urlparse(normalized_url)
normalized_password = parsed_normalized.password or ""

print(f"\n📋 NORMALIZED DATABASE_URL (after db.py processing):")
print(f"   {normalized_url[:50]}...")

print(f"\n🔍 NORMALIZED PASSWORD (after make_url processing):")
print(f"   Raw: {normalized_password}")
print(f"   Length: {len(normalized_password)} characters")
if normalized_password:
    print(f"   First 4 chars: {normalized_password[:4]}")
    print(f"   Last 4 chars: {normalized_password[-4:]}")
    
    # Check if it's URL encoded
    decoded = unquote(normalized_password)
    if decoded != normalized_password:
        print(f"   ⚠️  URL-encoded! Decoded: {decoded}")
    else:
        print(f"   ✅ Not URL-encoded")

# Compare
print(f"\n🔍 COMPARISON:")
if original_password == normalized_password:
    print(f"   ✅ Passwords MATCH - password is NOT being modified")
else:
    print(f"   ❌ Passwords DO NOT MATCH - password IS being modified!")
    print(f"   Original:  {original_password[:20]}...")
    print(f"   Normalized: {normalized_password[:20]}...")
    
    # Try to see what make_url does
    print(f"\n   🔍 Testing make_url() behavior:")
    try:
        test_url = make_url(raw_url.split("?")[0])
        reconstructed = str(test_url)
        print(f"   make_url() result: {reconstructed[:50]}...")
        
        # Parse reconstructed
        parsed_recon = urlparse(reconstructed)
        recon_password = parsed_recon.password or ""
        print(f"   Password in reconstructed: {recon_password[:20]}...")
        
        if recon_password != original_password:
            print(f"   ⚠️  make_url() is modifying the password!")
    except Exception as e:
        print(f"   Error testing make_url(): {e}")

print(f"\n" + "="*70)
print("💡 If passwords don't match, the issue is in _normalize_database_url()")
print("💡 Solution: Use the ORIGINAL password from Render, not the normalized one")
print("="*70)

