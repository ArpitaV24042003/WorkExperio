# from pydantic import BaseModel, EmailStr
# from typing import List, Optional
# from datetime import datetime

# # --- User Schemas ---
# class UserBase(BaseModel):
#     name: str
#     email: EmailStr

# class UserCreate(UserBase):
#     password: str

# class UserOut(UserBase):
#     id: int
#     class Config:
#         from_attributes = True

# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str

# # --- Resume Schemas ---
# class ResumeIn(BaseModel):
#     user_id: int
#     resume_text: str # This is for processing, may not be stored in SQL
#     file_url: Optional[str] = None

# class ResumeOut(BaseModel):
#     id: int
#     user_id: int
#     file_url: Optional[str]
#     parsed_mongo_id: Optional[str]
#     uploaded_at: datetime
#     class Config:
#         from_attributes = True

# # --- Team Schemas ---
# class TeamBase(BaseModel):
#     name: str
#     description: Optional[str] = None

# class TeamCreate(TeamBase):
#     pass

# class TeamOut(TeamBase):
#     id: int
#     class Config:
#         from_attributes = True

# # --- Project Schemas ---
# class ProjectBase(BaseModel):
#     title: str
#     description: Optional[str] = None
#     technologies: Optional[str] = None

# class ProjectCreate(ProjectBase):
#     user_id: int

# class ProjectOut(ProjectBase):
#     id: int
#     user_id: int
#     class Config:
#         from_attributes = True

# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# =========================
# User & Auth Schemas
# =========================

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    is_available_for_team: bool
    preferred_domain_id: Optional[int] = None

    class Config:
        from_attributes = True

# NEW: For setting user availability
class UserAvailability(BaseModel):
    is_available_for_team: bool
    preferred_domain_id: Optional[int] = None

# =========================
# Resume & Personal Schemas
# =========================

class ResumeIn(BaseModel):
    user_id: int
    file_url: str
    resume_text: Optional[str] = None # From your original crud

class ResumeOut(BaseModel):
    id: int
    user_id: int
    file_url: str
    is_verified: bool

    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    user_id: int # This is for a PERSONAL project
    title: str
    description: Optional[str] = None
    technologies: Optional[str] = None

class ProjectOut(ProjectCreate):
    id: int

    class Config:
        from_attributes = True

# =========================
# Team & Domain Schemas
# =========================

class TeamCreate(BaseModel):
    name: str

class TeamOut(TeamCreate):
    id: int
    # This will be populated automatically when you fetch a team
    chat_room: Optional[dict] = None 

    class Config:
        from_attributes = True

# NEW: For team_formation.py config
class DomainCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DomainOut(DomainCreate):
    id: int
    class Config:
        from_attributes = True

# NEW: For team_formation.py config
class RoleCreate(BaseModel):
    name: str
    domain_id: int
    required_skill_ids: List[int] = [] # List of Skill IDs

class RoleOut(BaseModel):
    id: int
    name: str
    domain_id: int
    class Config:
        from_attributes = True

# =========================
# Team Project Schemas
# =========================

# NEW: For team_ps_selection.py output
class TeamProjectCreate(BaseModel):
    project_name: str
    description: str
    project_plan_json: Optional[str] = None # This will hold the JSON plan

class TeamProjectOut(TeamProjectCreate):
    id: int
    team_id: int
    status: str
    class Config:
        from_attributes = True

# =========================
# Chat Schemas
# =========================

# NEW: For chat endpoints
class MessageCreate(BaseModel):
    content: str
    user_id: int

class MessageOut(BaseModel):
    id: int
    content: str
    user_id: int
    room_id: int
    timestamp: datetime 

    class Config:
        from_attributes = True