from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class BaseSchema(BaseModel):
	class Config:
		from_attributes = True


class UserCreate(BaseModel):
	name: str
	email: EmailStr
	password: str = Field(min_length=6)


class UserLogin(BaseModel):
	email: EmailStr
	password: str


class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"


class ResumeUploadResponse(BaseModel):
	id: str
	filename: str
	uploaded_at: datetime


class ResumeRead(BaseSchema):
	id: str
	user_id: str
	filename: str
	uploaded_at: datetime
	parsed_json: Dict[str, Any]


class EducationBase(BaseModel):
	institution: str
	degree: str
	field: str
	start_date: Optional[str] = None
	end_date: Optional[str] = None


class EducationCreate(EducationBase):
	pass


class EducationRead(BaseSchema, EducationBase):
	id: str
	user_id: str


class ExperienceBase(BaseModel):
	company: str
	role: str
	description: Optional[str] = None
	start_date: Optional[str] = None
	end_date: Optional[str] = None


class ExperienceCreate(ExperienceBase):
	pass


class ExperienceRead(BaseSchema, ExperienceBase):
	id: str
	user_id: str


class SkillBase(BaseModel):
	name: str
	level: Optional[str] = None


class SkillCreate(SkillBase):
	pass


class SkillRead(BaseSchema, SkillBase):
	id: str
	user_id: str


class UserProfileUpdate(BaseModel):
	name: Optional[str] = None
	profile_completed: Optional[bool] = None


class UserProfileRead(BaseSchema):
	id: str
	name: str
	email: EmailStr
	profile_completed: bool
	xp_points: int
	resumes: List[ResumeRead]
	educations: List[EducationRead]
	experiences: List[ExperienceRead]
	skills: List[SkillRead]


class UserSummary(BaseSchema):
	id: str
	name: str
	email: EmailStr
	profile_completed: bool
	xp_points: int
	level: Optional[str] = None


class ProjectBase(BaseModel):
	title: str
	description: str


class ProjectCreate(ProjectBase):
	ai_generated: bool = False
	team_type: str = "none"


class ProjectRead(BaseSchema, ProjectBase):
	id: str
	owner_id: str
	team_id: Optional[str] = None
	team_type: str
	ai_generated: bool
	created_at: datetime


class CandidateProfile(BaseModel):
	user_id: str
	skills: List[str] = []


class TeamSuggestionRequest(BaseModel):
	project_id: str
	required_skills: List[str] = []
	candidate_profiles: List[CandidateProfile] = []


class TeamAssignRequest(BaseModel):
	project_id: str
	user_ids: List[str]
	role_map: Optional[Dict[str, str]] = None


class TeamRead(BaseSchema):
	id: str
	project_id: str
	created_at: datetime


class TeamMemberRead(BaseSchema):
	id: str
	team_id: str
	user_id: str
	role: Optional[str]
	joined_at: datetime


class WaitlistEntryRead(BaseSchema):
	id: str
	project_id: str
	user_id: str
	created_at: datetime


class WaitlistRequest(BaseModel):
	user_id: str


class ChatMessageCreate(BaseModel):
	project_id: str
	user_id: str
	content: str


class ChatMessageRead(BaseSchema):
	id: str
	project_id: str
	user_id: str
	content: str
	created_at: datetime


class AssistantChatRequest(BaseModel):
	project_id: str
	user_id: str
	message: str


class AssistantChatResponse(BaseModel):
	response: str
	suggestions: List[str] = []


class PerformanceAnalysisResponse(BaseModel):
	participation_score: float
	task_consistency_score: float
	communication_score: float
	review_summary: Dict[str, Any]
	total_xp_awarded: int


class XPUpdateRequest(BaseModel):
	points: int
	reason: Optional[str] = None


class ReviewRequest(BaseModel):
	reviewer_id: str
	rating: int = Field(ge=1, le=5)
	comment: Optional[str] = None


class MetricsResponse(BaseModel):
	total_requests: int
	average_duration_ms: float
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
        