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
	project_id: Optional[str] = None  # Optional for pre-project team formation
	required_skills: List[str] = []
	candidate_profiles: List[CandidateProfile] = []


class TeamAssignRequest(BaseModel):
	project_id: str
	user_ids: List[str]
	role_map: Optional[Dict[str, str]] = None
	task_map: Optional[Dict[str, str]] = None  # Map of user_id to assigned task


class TeamRead(BaseSchema):
	id: str
	project_id: str
	created_at: datetime


class TeamMemberRead(BaseSchema):
	id: str
	team_id: str
	user_id: str
	role: Optional[str]
	task: Optional[str]  # Assigned task
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
	project_id: Optional[str] = None
	user_id: str
	message: str
	conversation_history: Optional[List[Dict[str, str]]] = []  # Previous messages for context


class AssistantChatResponse(BaseModel):
	response: str
	suggestions: List[str] = []
	conversation_id: Optional[str] = None  # For tracking conversation


class AIConversationRead(BaseSchema):
	id: str
	user_id: str
	project_id: Optional[str] = None
	role: str
	content: str
	created_at: datetime


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
