"""
Create environment variable templates for Render deployment
"""
import os
from pathlib import Path

def generate_secret_key():
    """Generate a random secret key"""
    import secrets
    return secrets.token_urlsafe(32)

def main():
    print("🔧 Creating Render Environment Variable Templates")
    print("=" * 60)
    print()
    
    # Backend environment variables
    backend_vars = {
        "SECRET_KEY": generate_secret_key(),
        "DATABASE_URL": "<FROM_POSTGRES_DATABASE_INTERNAL_URL>",
        "ALLOW_ORIGINS": "https://workexperio-frontend.onrender.com",
        "ENV": "production",
        "LOG_LEVEL": "INFO",
        "MONGO_URL": "<OPTIONAL_MONGODB_URL>",
        "MONGO_DB_NAME": "workexperio_db",
        "GITHUB_CLIENT_ID": "<OPTIONAL_GITHUB_CLIENT_ID>",
        "GITHUB_CLIENT_SECRET": "<OPTIONAL_GITHUB_CLIENT_SECRET>",
        "BACKEND_BASE_URL": "https://workexperio-backend.onrender.com",
        "FRONTEND_URL": "https://workexperio-frontend.onrender.com"
    }
    
    # Frontend environment variables
    frontend_vars = {
        "VITE_API_URL": "https://workexperio-backend.onrender.com",
        "VITE_WS_URL": "wss://workexperio-backend.onrender.com"
    }
    
    # Create backend env template
    backend_template = Path("render_backend_env.txt")
    with open(backend_template, "w") as f:
        f.write("# Backend Environment Variables for Render\n")
        f.write("# Copy these to your Render backend service\n")
        f.write("# Replace <PLACEHOLDERS> with actual values\n")
        f.write("\n")
        for key, value in backend_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"✅ Created: {backend_template}")
    
    # Create frontend env template
    frontend_template = Path("render_frontend_env.txt")
    with open(frontend_template, "w") as f:
        f.write("# Frontend Environment Variables for Render\n")
        f.write("# Copy these to your Render frontend static site\n")
        f.write("# Update URLs after deployment\n")
        f.write("\n")
        for key, value in frontend_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"✅ Created: {frontend_template}")
    print()
    print("📋 Next steps:")
    print("1. Copy values from render_backend_env.txt to Render backend service")
    print("2. Copy values from render_frontend_env.txt to Render frontend service")
    print("3. Update DATABASE_URL with actual PostgreSQL Internal URL")
    print("4. Update ALLOW_ORIGINS and URLs after deployment")

if __name__ == "__main__":
    main()

