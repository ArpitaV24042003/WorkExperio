# from fastapi import APIRouter
# from app.mongo import resume_raw, ai_evaluation

# router = APIRouter()

# @router.post("/resume_raw/")
# def save_parsed_resume(data: dict):
#     resume_raw.insert_one(data)
#     return {"message": "Parsed resume saved"}

# @router.post("/ai_evaluation/")
# def save_ai_results(data: dict):
#     ai_evaluation.insert_one(data)
#     return {"message": "AI evaluation saved"}


# routers/mongo_routes.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()

# Mock Mongo saving function
@router.post("/resume_raw/")
def save_parsed_resume(data: Dict[str, Any]):
    # Here you can insert data into MongoDB
    return {"message": "Parsed resume saved"}

@router.post("/ai_evaluation/")
def save_ai_results(data: Dict[str, Any]):
    # Save AI evaluation results to MongoDB
    return {"message": "AI evaluation saved"}
