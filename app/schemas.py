from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    class Config: from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ResumeIn(BaseModel):
    user_id: int
    resume_text: str
    file_url: Optional[str] = None

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamOut(TeamBase):
    id: int
    class Config:
        from_attributes = True