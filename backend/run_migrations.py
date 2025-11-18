"""
Run Alembic migrations for PostgreSQL on Render
This script can be run during deployment or manually
"""
import os
import sys
import subprocess

def run_migrations():
    """Run Alembic migrations"""
    print("🔄 Running database migrations...")
    
    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("⚠️  DATABASE_URL environment variable not set")
        print("⚠️  Skipping migrations")
        return False
    
    try:
        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)

