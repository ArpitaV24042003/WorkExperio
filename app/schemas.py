from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    class Config: from_attributes = True

class ResumeIn(BaseModel):
    user_id: int
    resume_text: str
    file_url: Optional[str] = None
