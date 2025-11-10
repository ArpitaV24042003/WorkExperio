# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import jwt

from app.database import get_db
from app import models

# config
JWT_SECRET = os.getenv("JWT_SECRET", "change_this_in_prod")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

router = APIRouter()
# simple password hashing
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def get_password_hash(password):
    return pwd_context.hash(password)


class RegisterSchema(BaseModel):
    name: str
    email: str
    password: str


class LoginSchema(BaseModel):
    email: str
    password: str


def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/register")
def register(payload: RegisterSchema, db: Session = Depends(get_db)):
    # check existing
    existing = db.query(models.User).filter(models.User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        name=payload.name,
        email=payload.email.lower(),
        password=get_password_hash(payload.password),
        profile_complete=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "registered", "user": {"id": user.id, "email": user.email, "name": user.name}}


@router.post("/login")
def login(payload: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email.lower()).first()
    if not user or not user.password or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    # build minimal user payload for frontend
    user_obj = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "profileComplete": user.profile_complete,
        "parsedResumeMongoId": user.parsed_resume_mongo_id,
        "parsedResumeSummary": user.parsed_resume_summary,
        "createdAt": user.__dict__.get("created_at"),
    }
    return {"token": token, "user": user_obj}


@router.get("/me")
def me(current_user: models.User = Depends(get_current_user)):
    user = current_user
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "profileComplete": user.profile_complete,
        "parsedResumeMongoId": user.parsed_resume_mongo_id,
        "parsedResumeSummary": user.parsed_resume_summary,
    }


@router.patch("/me")
def update_me(data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")

    # apply allowed updates
    allowed = {"name", "profile_complete", "parsed_resume_mongo_id", "parsed_resume_summary", "avatar_url"}
    for k, v in data.items():
        if k in allowed:
            setattr(user, k, v)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "profileComplete": user.profile_complete,
        "parsedResumeMongoId": user.parsed_resume_mongo_id,
        "parsedResumeSummary": user.parsed_resume_summary,
    }
