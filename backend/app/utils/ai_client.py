# backend/app/utils/ai_client.py
import os
import requests

# Base URL for your AI service (update if deployed)
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8081")

def ai_generate_team(payload: dict):
    """Send team formation data to the AI microservice"""
    r = requests.post(f"{AI_SERVICE_URL}/api/generate_team", json=payload, timeout=60)
    r.raise_for_status()
    return r.json().get("team")

def ai_predict_performance(payload: dict):
    """Send performance prediction data to the AI microservice"""
    r = requests.post(f"{AI_SERVICE_URL}/api/predict_performance", json=payload, timeout=60)
    r.raise_for_status()
    return r.json().get("performance")

def ai_parse_resume(file_path: str):
    """Upload a resume to the AI microservice for parsing"""
    with open(file_path, "rb") as f:
        r = requests.post(
            f"{AI_SERVICE_URL}/api/parse_resume",
            files={"file": f},
            timeout=120
        )
    r.raise_for_status()
    return r.json().get("parsed")
