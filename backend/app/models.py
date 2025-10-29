# from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean, Table
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.sql import func
# from .database import Base

# # -------------------------
# # Many-to-Many Relationships
# # -------------------------

# user_skill = Table(
#     "user_skill",
#     Base.metadata,
#     Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
#     Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
# )

# team_member = Table(
#     "team_member",
#     Base.metadata,
#     Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
#     Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
# )

# # -------------------------
# # Core Models
# # -------------------------

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100))
#     email = Column(String(100), unique=True, index=True)
#     password=Column(String, nullable=False)
#     resumes = relationship("Resume", back_populates="user")
#     skills = relationship("Skill", secondary=user_skill, back_populates="users")
#     phones = relationship("Phone", back_populates="user", cascade="all, delete-orphan")
#     links = relationship("Link", back_populates="user", cascade="all, delete-orphan")
#     education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
#     experiences = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
#     projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
#     certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")
#     teams = relationship("Team", secondary=team_member, back_populates="members")


# class Resume(Base):
#     __tablename__ = "resumes"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     file_url = Column(String(255))
#     parsed_mongo_id = Column(String(50))  # Reference to Mongo resume_parsed _id
#     uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
#     manual_additions = Column(Text, nullable=True)
#     is_verified = Column(Boolean, default=False)

#     user = relationship("User", back_populates="resumes")


# class Skill(Base):
#     __tablename__ = "skills"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), unique=True)

#     users = relationship("User", secondary=user_skill, back_populates="skills")


# # -------------------------
# # New Supporting Tables
# # -------------------------

# class Phone(Base):
#     __tablename__ = "phones"

#     id = Column(Integer, primary_key=True, index=True)
#     number = Column(String(20))
#     user_id = Column(Integer, ForeignKey("users.id"))

#     user = relationship("User", back_populates="phones")


# class Link(Base):
#     __tablename__ = "links"

#     id = Column(Integer, primary_key=True, index=True)
#     url = Column(String(255))
#     user_id = Column(Integer, ForeignKey("users.id"))

#     user = relationship("User", back_populates="links")


# class Education(Base):
#     __tablename__ = "education"

#     id = Column(Integer, primary_key=True, index=True)
#     institution = Column(String(255))
#     degree = Column(String(255))
#     start_date = Column(String(50))
#     end_date = Column(String(50))
#     user_id = Column(Integer, ForeignKey("users.id"))

#     user = relationship("User", back_populates="education")


# class Experience(Base):
#     __tablename__ = "experience"

#     id = Column(Integer, primary_key=True, index=True)
#     company = Column(String(255))
#     role = Column(String(255))
#     start_date = Column(String(50))
#     end_date = Column(String(50))
#     description = Column(Text)
#     user_id = Column(Integer, ForeignKey("users.id"))

#     user = relationship("User", back_populates="experiences")


# class Project(Base):
#     __tablename__ = "projects"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String(255))
#     description = Column(Text)
#     technologies = Column(Text)
#     user_id = Column(Integer, ForeignKey("users.id"))

#     user = relationship("User", back_populates="projects")


# class Certificate(Base):
#     __tablename__ = "certificates"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(255))
#     issuer = Column(String(255))
#     issue_date = Column(String(50))
#     user_id = Column(Integer, ForeignKey("users.id"))

#     user = relationship("User", back_populates="certificates")


# # -------------------------
# # Team & Project Management
# # -------------------------

# class Team(Base):
#     __tablename__ = "teams"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100))

#     members = relationship("User", secondary=team_member, back_populates="teams")
#     projects = relationship("ProjectAssignment", back_populates="team")


# class ProjectAssignment(Base):
#     __tablename__ = "project_assignments"

#     id = Column(Integer, primary_key=True, index=True)
#     project_name = Column(String(255))
#     description = Column(Text)
#     team_id = Column(Integer, ForeignKey("teams.id"))

#     team = relationship("Team", back_populates="projects")



from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from .database import Base

# -------------------------
# Many-to-Many Relationships
# -------------------------

# Links a User to their many Skills
user_skill = Table(
    "user_skill",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
)

# Links a Team to its many User members
team_member = Table(
    "team_member",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)

# NEW: Links a Role to its required Skills (for team_formation.py)
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
    password = Column(String, nullable=False)
    
    # --- Relationships from resume_parsing.py ---
    resumes = relationship("Resume", back_populates="user")
    skills = relationship("Skill", secondary=user_skill, back_populates="users")
    phones = relationship("Phone", back_populates="user", cascade="all, delete-orphan")
    links = relationship("Link", back_populates="user", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")
    
    # --- Relationships for team management ---
    teams = relationship("Team", secondary=team_member, back_populates="members")

    # --- NEW: For team_formation.py ---
    is_available_for_team = Column(Boolean, default=True)
    preferred_domain_id = Column(Integer, ForeignKey("domains.id"), nullable=True)
    preferred_domain = relationship("Domain")

    # --- NEW: For chat.py ---
    chat_messages = relationship("ChatMessage", back_populates="user")


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
    # NEW: Link skills to roles that require them
    roles = relationship("Role", secondary=role_skill, back_populates="required_skills")


# -------------------------
# Supporting Resume Tables
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


# ---------------------------------
# NEW: Domain/Role Config Models
# (Replaces hardcoded DOMAIN_CONFIG)
# ---------------------------------

class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True) # e.g., "Frontend Development"
    description = Column(Text, nullable=True)
    
    roles = relationship("Role", back_populates="domain")
    role_templates = relationship("DomainRoleTemplate", back_populates="domain")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True) # e.g., "Frontend Developer"
    domain_id = Column(Integer, ForeignKey("domains.id"))

    domain = relationship("Domain", back_populates="roles")
    required_skills = relationship("Skill", secondary=role_skill, back_populates="roles")
    domain_templates = relationship("DomainRoleTemplate", back_populates="role")

class DomainRoleTemplate(Base):
    __tablename__ = "domain_role_templates"
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))
    default_count = Column(Integer, nullable=False) # The "default_count" from your script

    domain = relationship("Domain", back_populates="role_templates")
    role = relationship("Role", back_populates="domain_templates")

# -------------------------
# Team & Project Management
# -------------------------

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))

    members = relationship("User", secondary=team_member, back_populates="teams")
    # UPDATED: Renamed relation
    projects = relationship("TeamProject", back_populates="team")
    # NEW: Link to the team's dedicated chat room
    chat_room = relationship("ChatRoom", back_populates="team", uselist=False, cascade="all, delete-orphan")


# UPDATED: Renamed from ProjectAssignment to TeamProject for clarity
class TeamProject(Base):
    __tablename__ = "team_projects" # Was "project_assignments"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255))
    description = Column(Text)
    team_id = Column(Integer, ForeignKey("teams.id"))
    
    # NEW: Store the output from team_ps_selection.py
    project_plan_json = Column(Text, nullable=True) # Stores the large generated JSON
    status = Column(String(50), default="Planning") # e.g., Planning, In-Progress, Completed
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)

    team = relationship("Team", back_populates="projects")


# -------------------------
# NEW: Chat Models
# -------------------------

class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), unique=True) # One room per team
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    team = relationship("Team", back_populates="chat_room")
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id")) # Who sent it
    room_id = Column(Integer, ForeignKey("chat_rooms.id")) # In which room
    
    user = relationship("User", back_populates="chat_messages")
    room = relationship("ChatRoom", back_populates="messages")