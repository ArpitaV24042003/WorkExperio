from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

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

# -------------------------
# Core Models
# -------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)

    resumes = relationship("Resume", back_populates="user")
    skills = relationship("Skill", secondary=user_skill, back_populates="users")
    phones = relationship("Phone", back_populates="user", cascade="all, delete-orphan")
    links = relationship("Link", back_populates="user", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")
    teams = relationship("Team", secondary=team_member, back_populates="members")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_url = Column(String(255))
    parsed_mongo_id = Column(String(50))  # Reference to Mongo resume_parsed _id
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    manual_additions = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)

    user = relationship("User", back_populates="resumes")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)

    users = relationship("User", secondary=user_skill, back_populates="skills")


# -------------------------
# New Supporting Tables
# -------------------------

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

    user = relationship("User", back_populates="projects")


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    issuer = Column(String(255))
    issue_date = Column(String(50))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="certificates")


# -------------------------
# Team & Project Management
# -------------------------

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))

    members = relationship("User", secondary=team_member, back_populates="teams")
    projects = relationship("ProjectAssignment", back_populates="team")


class ProjectAssignment(Base):
    __tablename__ = "project_assignments"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255))
    description = Column(Text)
    team_id = Column(Integer, ForeignKey("teams.id"))

    team = relationship("Team", back_populates="projects")
