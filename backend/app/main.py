# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from .database import Base, engine
# from  .import models

# Base.metadata.create_all(bind=engine)


# import sys, os

# # Add root path for imports
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # Routers
# from app.routers import (
#     mongo_routes,
#     projects,
#     users,
#     resumes,
#     chatbot,
#     teams,
#     # skills,
#     # projects,
#     # education,
#     # experience,
#     # certificates,
#     # links,
#     # phones
# )

# app = FastAPI(title="WorkExperio API")

# # Enable CORS so your React frontend can talk to FastAPI
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 🔑 in production restrict to your frontend URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ✅ Register routers
# app.include_router(mongo_routes.router, prefix="/mongo", tags=["MongoDB"])
# app.include_router(users.router, prefix="/users", tags=["Users"])
# app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
# app.include_router(chatbot.router, prefix="/chat", tags=["Chat"])
# app.include_router(teams.router, prefix="/teams", tags=["Teams"])
# app.include_router(projects.router, prefix="/projects", tags=["Projects"])
# # app.include_router(skills.router, prefix="/skills", tags=["Skills"])
# # app.include_router(education.router, prefix="/education", tags=["Education"])
# # app.include_router(experience.router, prefix="/experience", tags=["Experience"])
# # app.include_router(certificates.router, prefix="/certificates", tags=["Certificates"])
# # app.include_router(links.router, prefix="/links", tags=["Links"])
# # app.include_router(phones.router, prefix="/phones", tags=["Phones"])

# # Health check
# @app.get("/")
# def root():
#     return {"status": "ok", "service": "WorkExperio Backend"}

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add root path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine
from app.routers import (
    mongo_routes,
    projects,
    users,
    resumes,
    chatbot,
    teams,
)

# This is the new, robust way to handle startup tasks
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup
    print("Application startup: Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Application startup: Tables created successfully.")
    yield
    # This code runs on shutdown (not as important for us)
    print("Application shutdown.")

# We pass the lifespan function to the FastAPI app
app = FastAPI(title="WorkExperio API", lifespan=lifespan)

# Enable CORS so your React frontend can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all your routers
app.include_router(mongo_routes.router, prefix="/mongo")
app.include_router(users.router, prefix="/users")
app.include_router(resumes.router, prefix="/resumes")
app.include_router(chatbot.router, prefix="/chat")
app.include_router(teams.router, prefix="/teams")
app.include_router(projects.router, prefix="/projects")

# Health check
@app.get("/")
def root():
    return {"status": "ok", "service": "WorkExperio Backend"}
