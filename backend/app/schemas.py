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
	files_uploaded: int = 0
	files_contribution_score: float = 0.0
	review_summary: Dict[str, Any]
	total_xp_awarded: int
	images_count: int = 0  # Number of images uploaded
	images: List[Dict[str, Any]] = []  # List of image files for report display
	all_files: List[Dict[str, Any]] = []  # All files summary for report


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


class ProjectFileRead(BaseSchema):
	id: str
	project_id: str
	user_id: str
	filename: str
	file_path: str
	file_size: int
	file_type: Optional[str] = None
	mime_type: Optional[str] = None
	description: Optional[str] = None
	uploaded_at: datetime


class ProjectFileUploadResponse(BaseModel):
	id: str
	filename: str
	file_size: int
	uploaded_at: datetime
	message: str


# --- Task & Time tracking schemas ---


class TaskBase(BaseModel):
	title: str
	description: Optional[str] = None
	assignee_id: Optional[str] = None
	estimated_hours: Optional[float] = None
	status: Optional[str] = Field(default="todo")
	due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
	pass


class TaskUpdate(BaseModel):
	title: Optional[str] = None
	description: Optional[str] = None
	assignee_id: Optional[str] = None
	estimated_hours: Optional[float] = None
	status: Optional[str] = None
	due_date: Optional[datetime] = None


class TaskRead(BaseSchema, TaskBase):
	id: str
	project_id: str
	created_at: datetime
	completed_at: Optional[datetime] = None


class TimeLogRead(BaseSchema):
	id: str
	task_id: str
	user_id: Optional[str] = None
	start_time: datetime
	end_time: Optional[datetime] = None
	duration_minutes: Optional[int] = None
	created_at: datetime


class MemberAnalytics(BaseSchema):
	user_id: str
	tasks_completed: int
	total_hours: float
	code_quality_score: float
	project_id: Optional[str] = None
	# Extended metrics for richer analytics
	contribution_score: float = 0.0
	task_consistency_score: float = 0.0  # 0-100, on-time completion
	participation_score: float = 0.0    # 0-100 participation index
	communication_score: float = 0.0
	files_uploaded: int = 0
	messages_sent: int = 0
	ai_interactions: int = 0
	# Optional display name (filled from User table when available)
	user_name: Optional[str] = None


class TimelinePoint(BaseSchema):
	date: str
	completed_count: int


class ProjectAnalyticsOverview(BaseSchema):
	project_id: str
	total_tasks: int
	tasks_completed: int
	percent_complete: float
	overdue_tasks: int
	members: List[MemberAnalytics]
	timeline: List[TimelinePoint]
	avg_completion_minutes: float
	code_quality_average: float
	# Aggregate project metrics for dashboards
	total_member_hours: float = 0.0
	total_files_uploaded: int = 0
	total_messages: int = 0
	total_ai_interactions: int = 0
	# Project-level performance scores derived from the spec formulas
	on_time_rate: float = 0.0             # tasks_completed_on_time / tasks_total_completed
	delay_rate: float = 0.0               # tasks_completed_late / tasks_total_completed
	team_participation_score: float = 0.0 # aggregate 0–100
	team_performance_score: float = 0.0   # composite 0–100


class UserAnalyticsResponse(BaseSchema):
	user_id: str
	projects: List[MemberAnalytics]
	avg_completion_minutes: float
	on_time_completion_ratio: float
	code_quality_average: float


# --- AI task / role assignment ---


class AIAssignedTask(BaseModel):
	task_id: str
	task_title: str
	assignee_id: str
	assignee_score: float
	skill_match: float
	availability: float
	workload_penalty: float
	estimated_hours: float
	due_date: Optional[datetime] = None


class AIAssignmentPlan(BaseModel):
	project_id: str
	assignments: List[AIAssignedTask]
	# Lightweight rationale for UI display (human readable)
	rationale: List[str] = []


class AIProjectChatRequest(BaseModel):
	message: str


class AIProjectChatResponse(BaseSchema):
	reply: str
	id: str


class AIChatMessageRead(BaseSchema):
	id: str
	project_id: Optional[str] = None
	user_id: Optional[str] = None
	role: str
	content: str
	created_at: datetime


class CodeQualityAnalysisResponse(BaseSchema):
	score: float
	details: Dict[str, Any]
