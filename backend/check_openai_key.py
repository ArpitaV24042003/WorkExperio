"""
Quick diagnostic script to check if OpenAI API key is configured correctly.
Run this from the backend folder: python check_openai_key.py
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

print("=" * 60)
print("OpenAI API Key Diagnostic")
print("=" * 60)

# Check if .env file exists
if env_path.exists():
    print(f"✅ .env file found at: {env_path}")
else:
    print(f"❌ .env file NOT found at: {env_path}")
    print(f"   Expected location: {env_path}")
    print(f"   Please create it by copying env.example")

print()

# Check for API keys
api_key = os.getenv("OPENAI_API_KEY")
api_key_alt = os.getenv("OPENAI_API_KEY_WORKEXPERIO")

if api_key:
    preview = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 11 else api_key[:7] + "..."
    print(f"✅ OPENAI_API_KEY found: {preview}")
    print(f"   Length: {len(api_key)} characters")
    if not api_key.startswith("sk-"):
        print(f"   ⚠️  WARNING: API key should start with 'sk-'")
else:
    print(f"❌ OPENAI_API_KEY not found in environment")

if api_key_alt:
    preview = api_key_alt[:7] + "..." + api_key_alt[-4:] if len(api_key_alt) > 11 else api_key_alt[:7] + "..."
    print(f"✅ OPENAI_API_KEY_WORKEXPERIO found: {preview}")
else:
    print(f"ℹ️  OPENAI_API_KEY_WORKEXPERIO not set (optional)")

print()

# Test API key if available
active_key = api_key or api_key_alt
if active_key:
    print("Testing API key with OpenAI...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=active_key)
        
        # Make a simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=5
        )
        
        print("✅ API key is VALID and working!")
        print(f"   Response: {response.choices[0].message.content}")
        
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        
        print(f"❌ API key test FAILED")
        print(f"   Error Type: {error_type}")
        print(f"   Error Message: {error_msg}")
        
        if "401" in error_msg or "unauthorized" in error_msg.lower() or "invalid" in error_msg.lower():
            print("\n   🔴 ISSUE: Invalid API Key")
            print("   - Check if the key is correct")
            print("   - Get a new key from: https://platform.openai.com/api-keys")
            
        elif "429" in error_msg or "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
            print("\n   🔴 ISSUE: Quota/Billing Problem")
            print("   - Add billing method at: https://platform.openai.com/account/billing")
            print("   - Add credits to your account")
            print("   - Wait a few minutes and try again")
            
        elif "rate_limit" in error_msg.lower():
            print("\n   🟡 ISSUE: Rate Limit")
            print("   - Too many requests in a short time")
            print("   - Wait a few minutes and try again")
            
        else:
            print(f"\n   ⚠️  Unknown error: {error_msg}")
else:
    print("⚠️  No API key found to test")
    print("   Please add OPENAI_API_KEY to your .env file")

print()
print("=" * 60)
print("Next Steps:")
print("=" * 60)
print("1. If .env file is missing, create it:")
print("   copy env.example .env")
print()
print("2. Edit .env and add your API key:")
print("   OPENAI_API_KEY=sk-your-key-here")
print()
print("3. Restart your backend server after changing .env")
print("   (Stop with Ctrl+C, then restart)")
print()
print("4. Get a new API key from:")
print("   https://platform.openai.com/api-keys")
print()
print("5. Add billing/credits at:")
print("   https://platform.openai.com/account/billing")
print("=" * 60)

