"""
Automated Deployment Readiness Check
Verifies all files and configurations are ready for Render deployment
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    exists = Path(dirpath).is_dir()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {dirpath}")
    return exists

def check_file_content(filepath, required_strings, description):
    """Check if file contains required strings"""
    if not Path(filepath).exists():
        print(f"❌ {description}: File not found")
        return False
    
    content = Path(filepath).read_text(encoding='utf-8', errors='ignore')
    all_found = all(req in content for req in required_strings)
    status = "✅" if all_found else "⚠️"
    print(f"{status} {description}: {filepath}")
    if not all_found:
        missing = [req for req in required_strings if req not in content]
        print(f"   Missing: {', '.join(missing)}")
    return all_found

def main():
    print("=" * 60)
    print("🚀 WorkExperio - Deployment Readiness Check")
    print("=" * 60)
    print()
    
    checks = []
    
    # Critical files
    print("📁 Critical Files:")
    print("-" * 60)
    checks.append(check_file_exists("backend/requirements.txt", "Backend requirements"))
    checks.append(check_file_exists("backend/app/main.py", "Backend main file"))
    checks.append(check_file_exists("backend/init_db_production.py", "Production DB init script"))
    checks.append(check_file_exists("frontend/package.json", "Frontend package.json"))
    checks.append(check_file_exists("render.yaml", "Render config"))
    checks.append(check_file_exists("RENDER_DEPLOY.md", "Deployment guide"))
    print()
    
    # Backend structure
    print("🔧 Backend Structure:")
    print("-" * 60)
    checks.append(check_directory_exists("backend/app", "Backend app directory"))
    checks.append(check_directory_exists("backend/app/routers", "Routers directory"))
    checks.append(check_file_exists("backend/Dockerfile", "Backend Dockerfile"))
    checks.append(check_file_exists("backend/Procfile", "Backend Procfile"))
    print()
    
    # Frontend structure
    print("🎨 Frontend Structure:")
    print("-" * 60)
    checks.append(check_directory_exists("frontend/src", "Frontend src directory"))
    checks.append(check_directory_exists("frontend/src/pages", "Pages directory"))
    checks.append(check_file_exists("frontend/Dockerfile", "Frontend Dockerfile"))
    checks.append(check_file_exists("frontend/package.json", "Frontend package.json"))
    print()
    
    # Configuration files
    print("⚙️ Configuration Files:")
    print("-" * 60)
    checks.append(check_file_exists(".gitignore", "Git ignore"))
    checks.append(check_file_exists("docker-compose.yml", "Docker compose"))
    checks.append(check_file_exists("backend/runtime.txt", "Python runtime"))
    print()
    
    # Documentation
    print("📚 Documentation:")
    print("-" * 60)
    checks.append(check_file_exists("RENDER_DEPLOY.md", "Render deployment guide"))
    checks.append(check_file_exists("DEPLOYMENT_GUIDE.md", "Complete deployment guide"))
    checks.append(check_file_exists("DEPLOY_QUICK.md", "Quick deployment guide"))
    print()
    
    # Check backend main.py for PORT support
    print("🔍 Code Checks:")
    print("-" * 60)
    checks.append(check_file_content(
        "backend/app/main.py",
        ["PORT", "ALLOW_ORIGINS", "os.getenv"],
        "Backend supports environment variables"
    ))
    # Check requirements.txt more flexibly
    req_file = Path("backend/requirements.txt")
    if req_file.exists():
        req_content = req_file.read_text(encoding='utf-8', errors='ignore').lower()
        has_fastapi = "fastapi" in req_content
        has_uvicorn = "uvicorn" in req_content
        has_sqlalchemy = "sqlalchemy" in req_content
        all_deps = has_fastapi and has_uvicorn and has_sqlalchemy
        status = "✅" if all_deps else "⚠️"
        print(f"{status} Backend has core dependencies: backend/requirements.txt")
        if not all_deps:
            missing = []
            if not has_fastapi: missing.append("fastapi")
            if not has_uvicorn: missing.append("uvicorn")
            if not has_sqlalchemy: missing.append("sqlalchemy")
            print(f"   Missing: {', '.join(missing)}")
        checks.append(all_deps)
    else:
        print("❌ Backend has core dependencies: backend/requirements.txt (file not found)")
        checks.append(False)
    checks.append(check_file_content(
        "frontend/package.json",
        ["react", "vite"],
        "Frontend has core dependencies"
    ))
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print()
        print("✅ ALL CHECKS PASSED - Ready for deployment!")
        print()
        print("Next steps:")
        print("1. Follow RENDER_DEPLOY.md for manual deployment steps")
        print("2. Create PostgreSQL database on Render")
        print("3. Deploy backend service")
        print("4. Deploy frontend static site")
        return 0
    else:
        print()
        print(f"⚠️ {total - passed} check(s) failed")
        print("Please fix the issues above before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())

