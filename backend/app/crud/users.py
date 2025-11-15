# # crud/users.py
# from sqlalchemy.orm import Session
# from app import models
# from app.schemas import UserCreate
# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()

# def create_user(db: Session, user: UserCreate):
#     hashed_password = pwd_context.hash(user.password)
#     db_user = models.User(name=user.name, email=user.email, password=hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# def authenticate_user(db: Session, email: str, password: str):
#     user = get_user_by_email(db, email)
#     if not user:
#         return None
#     if not pwd_context.verify(password, user.password):
#         return None
#     return user

# def get_all_users(db: Session):
#     return db.query(models.User).all()

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .. import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(name=user.name, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_users(db: Session):
    return db.query(models.User).all()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        return None
    return user
