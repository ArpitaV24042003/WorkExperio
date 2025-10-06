from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- Resume Schemas ---
class ResumeIn(BaseModel):
    user_id: int
    resume_text: str # This is for processing, may not be stored in SQL
    file_url: Optional[str] = None

class ResumeOut(BaseModel):
    id: int
    user_id: int
    file_url: Optional[str]
    parsed_mongo_id: Optional[str]
    uploaded_at: datetime
    class Config:
        from_attributes = True

# --- Team Schemas ---
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamOut(TeamBase):
    id: int
    class Config:
        from_attributes = True

# --- Project Schemas ---
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: Optional[str] = None

class ProjectCreate(ProjectBase):
    user_id: int

class ProjectOut(ProjectBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True
