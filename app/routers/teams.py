from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_teams():
    return {"message": "List of teams will go here"}
