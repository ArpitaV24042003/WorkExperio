from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Corrected imports
from .. import schemas
from ..database import get_db
from ..crud import users as crud_users # Import the specific 'users' module from the 'crud' package

# Router setup without prefix
router = APIRouter(
    tags=["Users"] 
)

@router.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Use the specific import for the function call
    db_user = crud_users.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_users.create_user(db, user)

@router.post("/login", response_model=schemas.UserOut)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # Use the specific import for the function call
    db_user = crud_users.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return db_user

@router.get("/", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    # Use the specific import for the function call
    return crud_users.get_all_users(db)

