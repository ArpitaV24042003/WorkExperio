"""
End-to-End Tests for WorkExperio
Tests the complete user flow from signup to project creation
"""
import pytest
import requests
import json
from typing import Dict, Optional

# Base URL for API
BASE_URL = "http://localhost:8000"

class TestUser:
    """Helper class to manage test user state"""
    def __init__(self):
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.email: str = ""
        self.name: str = ""
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with auth token"""
        if not self.token:
            return {"Content-Type": "application/json"}
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

@pytest.fixture
def test_user():
    """Create a test user for E2E tests"""
    return TestUser()

@pytest.fixture
def api_client():
    """API client fixture"""
    return requests.Session()

class TestE2EFlow:
    """End-to-end test suite"""
    
    def test_1_health_check(self, api_client):
        """Test 1: API health check"""
        response = api_client.get(f"{BASE_URL}/docs")
        assert response.status_code in [200, 404], "API should be accessible"
        print("✅ Test 1: API is accessible")
    
    def test_2_user_signup(self, api_client, test_user):
        """Test 2: User signup"""
        import random
        import string
        
        # Generate unique email
        random_str = ''.join(random.choices(string.ascii_lowercase, k=6))
        test_user.email = f"test_{random_str}@example.com"
        test_user.name = f"Test User {random_str}"
        
        signup_data = {
            "name": test_user.name,
            "email": test_user.email,
            "password": "TestPassword123!"
        }
        
        response = api_client.post(
            f"{BASE_URL}/auth/signup",
            json=signup_data
        )
        
        assert response.status_code == 200 or response.status_code == 201, \
            f"Signup should succeed, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data or "token" in data, "Response should contain token"
        test_user.token = data.get("access_token") or data.get("token")
        print(f"✅ Test 2: User signed up - {test_user.email}")
    
    def test_3_user_login(self, api_client, test_user):
        """Test 3: User login"""
        if not test_user.email:
            pytest.skip("No user created in signup test")
        
        login_data = {
            "email": test_user.email,
            "password": "TestPassword123!"
        }
        
        response = api_client.post(
            f"{BASE_URL}/auth/login",
            json=login_data
        )
        
        assert response.status_code == 200, \
            f"Login should succeed, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data or "token" in data, "Response should contain token"
        test_user.token = data.get("access_token") or data.get("token")
        print(f"✅ Test 3: User logged in")
    
    def test_4_get_user_profile(self, api_client, test_user):
        """Test 4: Get user profile"""
        if not test_user.token:
            pytest.skip("No auth token available")
        
        headers = test_user.get_headers()
        response = api_client.get(
            f"{BASE_URL}/users/me",
            headers=headers
        )
        
        assert response.status_code == 200, \
            f"Should get profile, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Profile should contain user id"
        assert "email" in data, "Profile should contain email"
        test_user.user_id = data.get("id")
        print(f"✅ Test 4: Retrieved user profile - ID: {test_user.user_id}")
    
    def test_5_create_education(self, api_client, test_user):
        """Test 5: Create education entry"""
        if not test_user.token or not test_user.user_id:
            pytest.skip("No auth token or user ID available")
        
        education_data = {
            "institution": "Test University",
            "degree": "Bachelor of Science",
            "field": "Computer Science",
            "start_date": "2020-01-01",
            "end_date": "2024-01-01"
        }
        
        headers = test_user.get_headers()
        response = api_client.post(
            f"{BASE_URL}/users/{test_user.user_id}/educations",
            json=education_data,
            headers=headers
        )
        
        assert response.status_code in [200, 201], \
            f"Should create education, got {response.status_code}: {response.text}"
        print("✅ Test 5: Created education entry")
    
    def test_6_create_experience(self, api_client, test_user):
        """Test 6: Create experience entry"""
        if not test_user.token or not test_user.user_id:
            pytest.skip("No auth token or user ID available")
        
        experience_data = {
            "company": "Test Company",
            "position": "Software Developer",
            "description": "Developed web applications",
            "start_date": "2023-01-01",
            "end_date": None
        }
        
        headers = test_user.get_headers()
        response = api_client.post(
            f"{BASE_URL}/users/{test_user.user_id}/experiences",
            json=experience_data,
            headers=headers
        )
        
        assert response.status_code in [200, 201], \
            f"Should create experience, got {response.status_code}: {response.text}"
        print("✅ Test 6: Created experience entry")
    
    def test_7_create_skill(self, api_client, test_user):
        """Test 7: Create skill"""
        if not test_user.token or not test_user.user_id:
            pytest.skip("No auth token or user ID available")
        
        skill_data = {
            "name": "Python",
            "level": "intermediate"
        }
        
        headers = test_user.get_headers()
        response = api_client.post(
            f"{BASE_URL}/users/{test_user.user_id}/skills",
            json=skill_data,
            headers=headers
        )
        
        assert response.status_code in [200, 201], \
            f"Should create skill, got {response.status_code}: {response.text}"
        print("✅ Test 7: Created skill")
    
    def test_8_create_project(self, api_client, test_user):
        """Test 8: Create project"""
        if not test_user.token:
            pytest.skip("No auth token available")
        
        project_data = {
            "title": "E2E Test Project",
            "description": "This is a test project created during E2E testing",
            "team_type": "solo"
        }
        
        headers = test_user.get_headers()
        response = api_client.post(
            f"{BASE_URL}/projects",
            json=project_data,
            headers=headers
        )
        
        assert response.status_code in [200, 201], \
            f"Should create project, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Project should have an ID"
        project_id = data.get("id")
        print(f"✅ Test 8: Created project - ID: {project_id}")
        return project_id
    
    def test_9_list_projects(self, api_client, test_user):
        """Test 9: List user projects"""
        if not test_user.token:
            pytest.skip("No auth token available")
        
        headers = test_user.get_headers()
        response = api_client.get(
            f"{BASE_URL}/projects",
            headers=headers
        )
        
        assert response.status_code == 200, \
            f"Should list projects, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Projects should be a list"
        print(f"✅ Test 9: Listed projects - Found {len(data)} project(s)")
    
    def test_10_get_xp_points(self, api_client, test_user):
        """Test 10: Get XP points"""
        if not test_user.token or not test_user.user_id:
            pytest.skip("No auth token or user ID available")
        
        headers = test_user.get_headers()
        response = api_client.get(
            f"{BASE_URL}/users/{test_user.user_id}",
            headers=headers
        )
        
        assert response.status_code == 200, \
            f"Should get user, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "xp_points" in data, "User should have XP points"
        xp = data.get("xp_points", 0)
        print(f"✅ Test 10: Retrieved XP points - {xp} XP")
    
    def test_11_metrics_endpoint(self, api_client):
        """Test 11: Check metrics endpoint"""
        response = api_client.get(f"{BASE_URL}/metrics")
        # Metrics might require auth or might be public
        assert response.status_code in [200, 401, 403], \
            f"Metrics endpoint should respond, got {response.status_code}"
        print("✅ Test 11: Metrics endpoint accessible")

def run_e2e_tests():
    """Run all E2E tests"""
    print("🚀 Starting End-to-End Tests for WorkExperio")
    print("=" * 50)
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print("✅ Backend server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running!")
        print("   Please start the backend server first:")
        print("   cd backend && uvicorn app.main:app --reload")
        return False
    
    print()
    print("Running pytest...")
    print()
    
    # Run pytest
    import sys
    exit_code = pytest.main([
        __file__,
        "-v",
        "-s",  # Show print statements
        "--tb=short"
    ])
    
    return exit_code == 0

if __name__ == "__main__":
    success = run_e2e_tests()
    exit(0 if success else 1)

