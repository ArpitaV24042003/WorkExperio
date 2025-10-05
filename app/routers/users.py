from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, Base, engine
from app import models, schemas

router = APIRouter()

Base.metadata.create_all(bind=engine)  # ensure tables exist

@router.post("/", response_model=schemas.UserOut)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(400, "Email already exists")
    u = models.User(name=user_in.name, email=user_in.email)
    db.add(u); db.commit(); db.refresh(u)
    return u

@router.get("/", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()
