import requests
import os

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

def get_recommendations(user_id: int):
    response = requests.get(f"{AI_SERVICE_URL}/recommend/{user_id}")
    return response.json()
