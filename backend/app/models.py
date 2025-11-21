from __future__ import annotations

from datetime import datetime
from typing import Optional

import uuid
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from .db import Base


def uuid_pk() -> str:
	"""Generate UUID as string for SQLite compatibility"""
	return str(uuid.uuid4())


class User(Base):
	__tablename__ = "users"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	name: Mapped[str] = mapped_column(String(255))
	email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
	password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Nullable for OAuth users
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	profile_completed: Mapped[bool] = mapped_column(Boolean, default=False)
	xp_points: Mapped[int] = mapped_column(Integer, default=0)
	
	# OAuth fields
	github_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
	avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
	auth_provider: Mapped[str] = mapped_column(String(50), default="local")

	resumes: Mapped[list["Resume"]] = relationship(back_populates="user", cascade="all, delete-orphan")
	educations: Mapped[list["Education"]] = relationship(back_populates="user", cascade="all, delete-orphan")
	experiences: Mapped[list["Experience"]] = relationship(back_populates="user", cascade="all, delete-orphan")
	skills: Mapped[list["Skill"]] = relationship(back_populates="user", cascade="all, delete-orphan")
	stats: Mapped[Optional["UserStats"]] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")


class Resume(Base):
	__tablename__ = "resumes"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
	filename: Mapped[str] = mapped_column(String(255))
	uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	parsed_json: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict)

	user: Mapped["User"] = relationship(back_populates="resumes")


class Education(Base):
	__tablename__ = "educations"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
	institution: Mapped[str] = mapped_column(String(255))
	degree: Mapped[str] = mapped_column(String(255))
	field: Mapped[str] = mapped_column(String(255))
	start_date: Mapped[Optional[str]] = mapped_column(String(30))
	end_date: Mapped[Optional[str]] = mapped_column(String(30))

	user: Mapped["User"] = relationship(back_populates="educations")


class Experience(Base):
	__tablename__ = "experiences"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
	company: Mapped[str] = mapped_column(String(255))
	role: Mapped[str] = mapped_column(String(255))
	description: Mapped[Optional[str]] = mapped_column(Text)
	start_date: Mapped[Optional[str]] = mapped_column(String(30))
	end_date: Mapped[Optional[str]] = mapped_column(String(30))

	user: Mapped["User"] = relationship(back_populates="experiences")


class Skill(Base):
	__tablename__ = "skills"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
	name: Mapped[str] = mapped_column(String(255))
	level: Mapped[Optional[str]] = mapped_column(String(50))

	user: Mapped["User"] = relationship(back_populates="skills")


class Project(Base):
	__tablename__ = "projects"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	title: Mapped[str] = mapped_column(String(255))
	description: Mapped[str] = mapped_column(Text)
	owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
	team_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("teams.id"), nullable=True)
	team_type: Mapped[str] = mapped_column(String(20), default="none")
	ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Team(Base):
	__tablename__ = "teams"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	members: Mapped[list["TeamMember"]] = relationship(back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
	__tablename__ = "team_members"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id"))
	user_id: Mapped[str] = mapped_column(String(36))
	role: Mapped[Optional[str]] = mapped_column(String(100))
	task: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Assigned task for this team member
	joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	team: Mapped["Team"] = relationship(back_populates="members")


class ProjectWaitlist(Base):
	__tablename__ = "project_waitlists"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
	user_id: Mapped[str] = mapped_column(String(36))
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
	__tablename__ = "chat_messages"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
	user_id: Mapped[str] = mapped_column(String(36))
	content: Mapped[str] = mapped_column(Text)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AIConversation(Base):
	__tablename__ = "ai_conversations"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
	project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id"), nullable=True)
	role: Mapped[str] = mapped_column(String(20))  # "user" or "assistant"
	content: Mapped[str] = mapped_column(Text)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserStats(Base):
	__tablename__ = "user_stats"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
	total_xp: Mapped[int] = mapped_column(Integer, default=0)
	tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
	files_uploaded: Mapped[int] = mapped_column(Integer, default=0)  # Track file uploads as metric
	reviews_received: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict)
	ai_score: Mapped[float] = mapped_column(Float, default=0.0)
	updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

	user: Mapped["User"] = relationship(back_populates="stats")


class ModelPrediction(Base):
	__tablename__ = "model_predictions"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id"), nullable=True)
	model_name: Mapped[str] = mapped_column(String(255))
	input_json: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict)
	output_json: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict)
	score: Mapped[Optional[float]] = mapped_column(Float)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProjectFile(Base):
	__tablename__ = "project_files"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
	user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
	filename: Mapped[str] = mapped_column(String(255))
	file_path: Mapped[str] = mapped_column(String(500))
	file_size: Mapped[int] = mapped_column(Integer)  # Size in bytes
	file_type: Mapped[Optional[str]] = mapped_column(String(50))  # e.g., "code", "document", "folder"
	mime_type: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., "text/plain", "application/zip"
	description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Task(Base):
	"""Per-project task with time allotment and basic workflow status."""

	__tablename__ = "tasks"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"))
	title: Mapped[str] = mapped_column(String(255))
	description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	assignee_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
	estimated_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	status: Mapped[str] = mapped_column(String(50), default="todo")  # todo / in_progress / done
	due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
	completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class TimeLog(Base):
	"""Time tracking entries for tasks."""

	__tablename__ = "timelogs"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"))
	user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
	start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
	end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
	duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProjectContribution(Base):
	"""Aggregate contribution metrics per user per project."""

	__tablename__ = "project_contributions"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"))
	user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
	tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
	total_hours: Mapped[float] = mapped_column(Float, default=0.0)
	code_quality_score: Mapped[float] = mapped_column(Float, default=0.0)  # placeholder 0-100
	last_updated: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
	)


class AIChatMessage(Base):
	"""Lightweight chat history for per-project AI assistant."""

	__tablename__ = "ai_chat_messages"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id"), nullable=True)
	user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
	role: Mapped[str] = mapped_column(String(10))  # user/assistant/system
	content: Mapped[str] = mapped_column(Text)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

