# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List

# # Corrected imports
# from .. import schemas
# from ..database import get_db
# from ..crud import users as crud_users # Import the specific 'users' module from the 'crud' package

# # Router setup without prefix
# router = APIRouter(
#     tags=["Users"] 
# )

# @router.post("/register", response_model=schemas.UserOut)
# def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     # Use the specific import for the function call
#     db_user = crud_users.get_user_by_email(db, user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud_users.create_user(db, user)

# @router.post("/login", response_model=schemas.UserOut)
# def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
#     # Use the specific import for the function call
#     db_user = crud_users.authenticate_user(db, user.email, user.password)
#     if not db_user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     return db_user

# @router.get("/", response_model=List[schemas.UserOut])
# def list_users(db: Session = Depends(get_db)):
#     # Use the specific import for the function call
#     return crud_users.get_all_users(db)





from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel # Import BaseModel

# Corrected imports
from .. import schemas
from ..database import get_db
from ..crud import users as crud_users # Import the specific 'users' module from the 'crud' package
from .. import models # NEW: Import models

# Router setup without prefix
router = APIRouter(
    tags=["Users"] 
)

# --- NEW SCHEMA ---
# (You should move this to schemas.py)
class UserAvailability(BaseModel):
    is_available_for_team: bool
    preferred_domain_id: Optional[int] = None

#
# --- EXISTING ENDPOINTS (UNCHANGED) ---
#
@router.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud_users.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_users.create_user(db, user)

@router.post("/login", response_model=schemas.UserOut)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud_users.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return db_user

@router.get("/", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return crud_users.get_all_users(db)

#
# --- NEW ENDPOINT ---
#
@router.put("/{user_id}/availability", response_model=schemas.UserOut)
def set_user_availability(
    user_id: int, 
    availability: UserAvailability, 
    db: Session = Depends(get_db)
):
    """
    Set a user's availability for team formation and their preferred domain.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # If a domain ID is provided, check if it exists
    if availability.preferred_domain_id:
        domain = db.query(models.Domain).filter(models.Domain.id == availability.preferred_domain_id).first()
        if not domain:
            raise HTTPException(status_code=404, detail="Domain not found")
        db_user.preferred_domain_id = availability.preferred_domain_id
    else:
        db_user.preferred_domain_id = None
        
    db_user.is_available_for_team = availability.is_available_for_team
    
    db.commit()
    db.refresh(db_user)
    return db_user