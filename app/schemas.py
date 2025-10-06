from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

# ---------------- Users ----------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True  # ✅ Allows automatic conversion from SQLAlchemy models

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ---------------- Resumes ----------------
class ResumeIn(BaseModel):
    user_id: int
    resume_text: str
    file_url: Optional[str] = None

class ResumeOut(BaseModel):
    id: int
    user_id: int
    file_url: Optional[str]
    parsed_mongo_id: Optional[str]
    uploaded_at: Optional[str]
    manual_additions: Optional[str]
    is_verified: bool

    class Config:
        from_attributes = True

# ---------------- Teams ----------------
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None  # Optional field

class TeamCreate(TeamBase):
    pass

class TeamOut(TeamBase):
    id: int

    class Config:
        from_attributes = True

# ---------------- Projects ----------------
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
