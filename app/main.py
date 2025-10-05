from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from  .import models

Base.metadata.create_all(bind=engine)


import sys, os

# Add root path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Routers
from app.routers import (
    mongo_routes,
    users,
    resumes,
    chatbot,
    teams,
    # skills,
    # projects,
    # education,
    # experience,
    # certificates,
    # links,
    # phones
)

app = FastAPI(title="WorkExperio API")

# Enable CORS so your React frontend can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔑 in production restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register routers
app.include_router(mongo_routes.router, prefix="/mongo", tags=["MongoDB"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
app.include_router(chatbot.router, prefix="/chat", tags=["Chat"])
app.include_router(teams.router, prefix="/teams", tags=["Teams"])
# app.include_router(skills.router, prefix="/skills", tags=["Skills"])
# app.include_router(projects.router, prefix="/projects", tags=["Projects"])
# app.include_router(education.router, prefix="/education", tags=["Education"])
# app.include_router(experience.router, prefix="/experience", tags=["Experience"])
# app.include_router(certificates.router, prefix="/certificates", tags=["Certificates"])
# app.include_router(links.router, prefix="/links", tags=["Links"])
# app.include_router(phones.router, prefix="/phones", tags=["Phones"])

# Health check
@app.get("/")
def root():
    return {"status": "ok", "service": "WorkExperio Backend"}
