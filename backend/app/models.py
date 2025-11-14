from __future__ import annotations

from datetime import datetime
from typing import Optional

import uuid
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from .db import Base


def uuid_pk() -> uuid.UUID:
	return uuid.uuid4()


class User(Base):
	__tablename__ = "users"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	name: Mapped[str] = mapped_column(String(255))
	email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
	password_hash: Mapped[str] = mapped_column(String(255))
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	profile_completed: Mapped[bool] = mapped_column(Boolean, default=False)
	xp_points: Mapped[int] = mapped_column(Integer, default=0)

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


class UserStats(Base):
	__tablename__ = "user_stats"

	id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid_pk()))
	user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True)
	total_xp: Mapped[int] = mapped_column(Integer, default=0)
	tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
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

# app/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    DateTime,
    Boolean,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# -------------------------
# Many-to-Many Relationships
# -------------------------

user_skill = Table(
    "user_skill",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
)

team_member = Table(
    "team_member",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)

role_skill = Table(
    "role_skill",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
)


# -------------------------
# Core Models
# -------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password = Column(String, nullable=True)

    github_id = Column(String(50), unique=True, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    auth_provider = Column(String(50), default="local")

    # Onboarding / resume flags used by frontend
    profile_complete = Column(Boolean, default=False, nullable=False)
    parsed_resume_mongo_id = Column(String(100), nullable=True)
    # A compact summary of parsed resume (JSON string) for quick frontend checks
    parsed_resume_summary = Column(Text, nullable=True)

    resumes = relationship("Resume", back_populates="user")
    skills = relationship("Skill", secondary=user_skill, back_populates="users")
    phones = relationship("Phone", back_populates="user", cascade="all, delete-orphan")
    links = relationship("Link", back_populates="user", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")
    teams = relationship("Team", secondary=team_member, back_populates="members")
    chat_messages = relationship("ChatMessage", back_populates="user")

    is_available_for_team = Column(Boolean, default=True)
    preferred_domain_id = Column(Integer, ForeignKey("domains.id"), nullable=True)
    preferred_domain = relationship("Domain")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_url = Column(String(255))
    parsed_mongo_id = Column(String(100))  # Reference to resume_parsed _id in MongoDB
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    manual_additions = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)

    user = relationship("User", back_populates="resumes")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)

    users = relationship("User", secondary=user_skill, back_populates="skills")
    roles = relationship("Role", secondary=role_skill, back_populates="required_skills")


class Phone(Base):
    __tablename__ = "phones"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(20))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="phones")


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="links")


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    institution = Column(String(255))
    degree = Column(String(255))
    start_date = Column(String(50))
    end_date = Column(String(50))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="education")


class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(255))
    role = Column(String(255))
    start_date = Column(String(50))
    end_date = Column(String(50))
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="experiences")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    technologies = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Additional fields to support teamPending / solo flow (for individual projects)
    team_pending = Column(Boolean, default=False)
    team_pending_until = Column(DateTime(timezone=True), nullable=True)
    solo_assigned = Column(Boolean, default=False)
    status = Column(String(50), default="draft")  # e.g., draft, team_pending, active, completed

    user = relationship("User", back_populates="projects")


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    issuer = Column(String(255))
    issue_date = Column(String(50))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="certificates")


# Domain / Role models (unchanged)
class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text, nullable=True)

    roles = relationship("Role", back_populates="domain")
    role_templates = relationship("DomainRoleTemplate", back_populates="domain")


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"))

    domain = relationship("Domain", back_populates="roles")
    required_skills = relationship("Skill", secondary=role_skill, back_populates="roles")
    domain_templates = relationship("DomainRoleTemplate", back_populates="role")


class DomainRoleTemplate(Base):
    __tablename__ = "domain_role_templates"
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))
    default_count = Column(Integer, nullable=False)

    domain = relationship("Domain", back_populates="role_templates")
    role = relationship("Role", back_populates="domain_templates")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))

    members = relationship("User", secondary=team_member, back_populates="teams")
    projects = relationship("TeamProject", back_populates="team")
    chat_room = relationship("ChatRoom", back_populates="team", uselist=False, cascade="all, delete-orphan")


class TeamProject(Base):
    __tablename__ = "team_projects"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255))
    description = Column(Text)
    team_id = Column(Integer, ForeignKey("teams.id"))

    project_plan_json = Column(Text, nullable=True)
    status = Column(String(50), default="Planning")
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)

    # New fields to track pending / solo assignment
    team_pending = Column(Boolean, default=False)
    team_pending_until = Column(DateTime(timezone=True), nullable=True)
    solo_assigned = Column(Boolean, default=False)

    team = relationship("Team", back_populates="projects")


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="chat_room")
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("chat_rooms.id"))

    user = relationship("User", back_populates="chat_messages")
    room = relationship("ChatRoom", back_populates="messages")
