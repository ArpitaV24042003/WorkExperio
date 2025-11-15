"""
Simple End-to-End Test Runner
Tests the complete user flow - can run against a running server
"""
import requests
import json
import sys
import time
from typing import Optional, Dict

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

class TestUser:
    def __init__(self):
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.email: str = ""
        self.name: str = ""
    
    def get_headers(self) -> Dict[str, str]:
        if not self.token:
            return {"Content-Type": "application/json"}
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

def test_1_check_server():
    """Test 1: Check if server is running"""
    print_info("Test 1: Checking if backend server is running...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code in [200, 404]:
            print_success("Backend server is accessible")
            return True
    except requests.exceptions.ConnectionError:
        print_error("Backend server is not running!")
        print_warning("Please start the backend: cd backend && uvicorn app.main:app --reload")
        return False
    return False

def test_2_user_signup(test_user: TestUser):
    """Test 2: User signup"""
    print_info("Test 2: Testing user signup...")
    import random
    import string
    
    random_str = ''.join(random.choices(string.ascii_lowercase, k=6))
    test_user.email = f"test_{random_str}@example.com"
    test_user.name = f"Test User {random_str}"
    
    signup_data = {
        "name": test_user.name,
        "email": test_user.email,
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json=signup_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            test_user.token = data.get("access_token") or data.get("token")
            if test_user.token:
                print_success(f"User signed up successfully: {test_user.email}")
                return True
            else:
                print_error("Signup succeeded but no token in response")
                return False
        else:
            print_error(f"Signup failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Signup error: {e}")
        return False

def test_3_user_login(test_user: TestUser):
    """Test 3: User login"""
    print_info("Test 3: Testing user login...")
    if not test_user.email:
        print_warning("Skipping login test - no user email")
        return False
    
    login_data = {
        "email": test_user.email,
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            test_user.token = data.get("access_token") or data.get("token")
            if test_user.token:
                print_success("User logged in successfully")
                return True
            else:
                print_error("Login succeeded but no token in response")
                return False
        else:
            print_error(f"Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Login error: {e}")
        return False

def test_4_get_profile(test_user: TestUser):
    """Test 4: Get user profile"""
    print_info("Test 4: Testing get user profile...")
    if not test_user.token:
        print_warning("Skipping profile test - no auth token")
        return False
    
    headers = test_user.get_headers()
    try:
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            test_user.user_id = data.get("id")
            if test_user.user_id:
                print_success(f"Retrieved user profile - ID: {test_user.user_id}")
                return True
            else:
                print_error("Profile retrieved but no user ID")
                return False
        else:
            print_error(f"Get profile failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Get profile error: {e}")
        return False

def test_5_create_education(test_user: TestUser):
    """Test 5: Create education"""
    print_info("Test 5: Testing create education...")
    if not test_user.token or not test_user.user_id:
        print_warning("Skipping education test - no auth token or user ID")
        return False
    
    education_data = {
        "institution": "Test University",
        "degree": "Bachelor of Science",
        "field": "Computer Science",
        "start_date": "2020-01-01",
        "end_date": "2024-01-01"
    }
    
    headers = test_user.get_headers()
    try:
        response = requests.post(
            f"{BASE_URL}/users/{test_user.user_id}/educations",
            json=education_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print_success("Created education entry")
            return True
        else:
            print_error(f"Create education failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Create education error: {e}")
        return False

def test_6_create_skill(test_user: TestUser):
    """Test 6: Create skill"""
    print_info("Test 6: Testing create skill...")
    if not test_user.token or not test_user.user_id:
        print_warning("Skipping skill test - no auth token or user ID")
        return False
    
    skill_data = {
        "name": "Python",
        "level": "intermediate"
    }
    
    headers = test_user.get_headers()
    try:
        response = requests.post(
            f"{BASE_URL}/users/{test_user.user_id}/skills",
            json=skill_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print_success("Created skill")
            return True
        else:
            print_error(f"Create skill failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Create skill error: {e}")
        return False

def test_7_create_project(test_user: TestUser):
    """Test 7: Create project"""
    print_info("Test 7: Testing create project...")
    if not test_user.token:
        print_warning("Skipping project test - no auth token")
        return False
    
    project_data = {
        "title": "E2E Test Project",
        "description": "This is a test project created during E2E testing",
        "team_type": "solo"
    }
    
    headers = test_user.get_headers()
    try:
        response = requests.post(
            f"{BASE_URL}/projects",
            json=project_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            project_id = data.get("id")
            print_success(f"Created project - ID: {project_id}")
            return True, project_id
        else:
            print_error(f"Create project failed: {response.status_code} - {response.text}")
            return False, None
    except Exception as e:
        print_error(f"Create project error: {e}")
        return False, None

def test_8_list_projects(test_user: TestUser):
    """Test 8: List projects"""
    print_info("Test 8: Testing list projects...")
    if not test_user.token:
        print_warning("Skipping list projects test - no auth token")
        return False
    
    headers = test_user.get_headers()
    try:
        response = requests.get(
            f"{BASE_URL}/projects",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 0
            print_success(f"Listed projects - Found {count} project(s)")
            return True
        else:
            print_error(f"List projects failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"List projects error: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 WorkExperio End-to-End Test Suite")
    print("=" * 60)
    print()
    
    test_user = TestUser()
    results = []
    
    # Run tests
    results.append(("Server Check", test_1_check_server()))
    if not results[-1][1]:
        print()
        print_error("Cannot continue - server is not running")
        return False
    
    print()
    results.append(("User Signup", test_2_user_signup(test_user)))
    print()
    results.append(("User Login", test_3_user_login(test_user)))
    print()
    results.append(("Get Profile", test_4_get_profile(test_user)))
    print()
    results.append(("Create Education", test_5_create_education(test_user)))
    print()
    results.append(("Create Skill", test_6_create_skill(test_user)))
    print()
    result = test_7_create_project(test_user)
    if isinstance(result, tuple):
        success, project_id = result
    else:
        success = result
    results.append(("Create Project", success))
    print()
    results.append(("List Projects", test_8_list_projects(test_user)))
    
    # Summary
    print()
    print("=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All tests passed! 🎉")
        return True
    else:
        print_error(f"{total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

