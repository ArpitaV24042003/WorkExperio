from datetime import datetime, timedelta, timezone
from typing import Optional
import warnings
import logging

from jose import jwt
from passlib.context import CryptContext

from .config import settings

# Suppress bcrypt version warning (known issue with passlib and newer bcrypt)
# This warning is harmless - passlib works fine with newer bcrypt versions
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)
logging.getLogger("passlib").setLevel(logging.ERROR)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
	return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
	if expires_delta is None:
		expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
	expire = datetime.now(timezone.utc) + expires_delta
	payload = {"sub": subject, "exp": expire}
	return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
	return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

