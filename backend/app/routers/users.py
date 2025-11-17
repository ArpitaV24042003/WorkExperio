from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import re

from ..db import get_db
from ..dependencies import get_current_user
from ..models import User, Resume, Education, Experience, Skill, UserStats
from ..schemas import (
	UserProfileRead,
	UserProfileUpdate,
	ResumeRead,
	EducationCreate,
	EducationRead,
	ExperienceCreate,
	ExperienceRead,
	SkillCreate,
	SkillRead,
	UserSummary,
)
from ..utils import calculate_level

router = APIRouter()


@router.get("/me", response_model=UserSummary)
def get_current_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	level = calculate_level(current_user.xp_points)
	return UserSummary(
		id=current_user.id,
		name=current_user.name,
		email=current_user.email,
		profile_completed=current_user.profile_completed,
		xp_points=current_user.xp_points,
		level=level,
	)


def assert_self(user_id: str, current_user: User):
	if current_user.id != user_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")


@router.get("/{user_id}/profile", response_model=UserProfileRead)
def get_profile(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	assert_self(user_id, current_user)
	user = (
		db.query(User)
		.filter(User.id == user_id)
		.options(
			# eager loading not shown; default lazy usage
		)
		.first()
	)
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

	return UserProfileRead(
		id=user.id,
		name=user.name,
		email=user.email,
		profile_completed=user.profile_completed,
		xp_points=user.xp_points,
		resumes=user.resumes,
		educations=user.educations,
		experiences=user.experiences,
		skills=user.skills,
	)


@router.patch("/{user_id}/profile", response_model=UserProfileRead)
def update_profile(
	user_id: str,
	payload: UserProfileUpdate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	assert_self(user_id, current_user)
	user = db.query(User).filter(User.id == user_id).first()
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

	if payload.name is not None:
		user.name = payload.name
	if payload.profile_completed is not None:
		user.profile_completed = payload.profile_completed

	db.commit()
	db.refresh(user)
	return get_profile(user_id, current_user, db)


@router.post("/{user_id}/profile/from-resume/{resume_id}", response_model=UserProfileRead)
def populate_from_resume(
	user_id: str,
	resume_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	assert_self(user_id, current_user)
	resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
	if not resume:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

	extracted = resume.parsed_json.get("extracted", {})
	user = db.query(User).filter(User.id == user_id).first()
	user.profile_completed = True

	db.query(Education).filter(Education.user_id == user_id).delete()
	db.query(Experience).filter(Experience.user_id == user_id).delete()
	db.query(Skill).filter(Skill.user_id == user_id).delete()

	# Format and add education entries
	for entry in extracted.get("education", []):
		# Try to parse education entry (format: "Institution - Degree in Field" or similar)
		entry_clean = entry.strip()
		if entry_clean:
			# Simple parsing - can be improved
			parts = entry_clean.split(" - ")
			institution = parts[0] if parts else entry_clean
			degree_field = " - ".join(parts[1:]) if len(parts) > 1 else ""
			db.add(Education(user_id=user_id, institution=institution, degree=degree_field, field=""))
	
	# Format and add experience entries
	for entry in extracted.get("experience", []):
		entry_clean = entry.strip()
		if entry_clean:
			# Simple parsing - can be improved
			parts = entry_clean.split(" - ")
			role = parts[0] if parts else entry_clean
			company = " - ".join(parts[1:]) if len(parts) > 1 else entry_clean
			db.add(Experience(user_id=user_id, company=company, role=role, description="Imported from resume"))
	
	# Format and add skills (split if multiple skills in one entry)
	for entry in extracted.get("skills", []):
		entry_clean = entry.strip()
		if entry_clean:
			# Split by common separators
			skills = [s.strip() for s in re.split(r'[,;|/•-]', entry_clean) if s.strip()]
			for skill in skills:
				if skill:
					db.add(Skill(user_id=user_id, name=skill))

	db.commit()
	return get_profile(user_id, current_user, db)


@router.get("/{user_id}/educations", response_model=list[EducationRead])
def list_educations(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	assert_self(user_id, current_user)
	return db.query(Education).filter(Education.user_id == user_id).all()


@router.post("/{user_id}/educations", response_model=EducationRead)
def create_education(
	user_id: str,
	payload: EducationCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	assert_self(user_id, current_user)
	education = Education(user_id=user_id, **payload.model_dump())
	db.add(education)
	db.commit()
	db.refresh(education)
	return education


@router.put("/{user_id}/educations/{education_id}", response_model=EducationRead)
def update_education(
	user_id: str,
	education_id: str,
	payload: EducationCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	assert_self(user_id, current_user)
	education = db.query(Education).filter(Education.id == education_id, Education.user_id == user_id).first()
	if not education:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education not found")

	for field, value in payload.model_dump().items():
		setattr(education, field, value)
	db.commit()
	db.refresh(education)
	return education


@router.delete("/{user_id}/educations/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(user_id: str, education_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	assert_self(user_id, current_user)
	deleted = db.query(Education).filter(Education.id == education_id, Education.user_id == user_id).delete()
	if not deleted:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education not found")
	db.commit()
	return None


@router.get("/{user_id}/experiences", response_model=list[ExperienceRead])
def list_experiences(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	assert_self(user_id, current_user)
	return db.query(Experience).filter(Experience.user_id == user_id).all()


@router.post("/{user_id}/experiences", response_model=ExperienceRead)
def create_experience(
	user_id: str,
	payload: ExperienceCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	assert_self(user_id, current_user)
	experience = Experience(user_id=user_id, **payload.model_dump())
	db.add(experience)
	db.commit()
	db.refresh(experience)
	return experience


@router.put("/{user_id}/experiences/{experience_id}", response_model=ExperienceRead)
def update_experience(
	user_id: str,
	experience_id: str,
	payload: ExperienceCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	assert_self(user_id, current_user)
	experience = db.query(Experience).filter(Experience.id == experience_id, Experience.user_id == user_id).first()
	if not experience:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")

	for field, value in payload.model_dump().items():
		setattr(experience, field, value)
	db.commit()
	db.refresh(experience)
	return experience


@router.delete("/{user_id}/experiences/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(user_id: str, experience_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	assert_self(user_id, current_user)
	deleted = db.query(Experience).filter(Experience.id == experience_id, Experience.user_id == user_id).delete()
	if not deleted:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
	db.commit()
	return None


@router.get("/{user_id}/skills", response_model=list[SkillRead])
def list_skills(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	assert_self(user_id, current_user)
	return db.query(Skill).filter(Skill.user_id == user_id).all()


@router.post("/{user_id}/skills", response_model=SkillRead)
def create_skill(user_id: str, payload: SkillCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	assert_self(user_id, current_user)
	skill = Skill(user_id=user_id, **payload.model_dump())
	db.add(skill)
	db.commit()
	db.refresh(skill)
	return skill


@router.put("/{user_id}/skills/{skill_id}", response_model=SkillRead)
def update_skill(
	user_id: str,
	skill_id: str,
	payload: SkillCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	assert_self(user_id, current_user)
	skill = db.query(Skill).filter(Skill.id == skill_id, Skill.user_id == user_id).first()
	if not skill:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

	for field, value in payload.model_dump().items():
		setattr(skill, field, value)
	db.commit()
	db.refresh(skill)
	return skill


@router.delete("/{user_id}/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(user_id: str, skill_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	assert_self(user_id, current_user)
	deleted = db.query(Skill).filter(Skill.id == skill_id, Skill.user_id == user_id).delete()
	if not deleted:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
	db.commit()
	return None


@router.get("/{user_id}/stats")
def get_stats(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	assert_self(user_id, current_user)
	stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
	if not stats:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stats not found")
	level = calculate_level(stats.total_xp)
	return {
		"user_id": user_id,
		"total_xp": stats.total_xp,
		"tasks_completed": stats.tasks_completed,
		"reviews_received": stats.reviews_received,
		"ai_score": stats.ai_score,
		"level": level,
	}


@router.get("/search/by-skills")
def search_users_by_skills(
	skills: str,  # Comma-separated skills
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	limit: int = 10,
):
	"""
	Search for users who have matching skills.
	Returns users with their skills for team matching.
	"""
	skill_list = [s.strip().lower() for s in skills.split(",") if s.strip()]
	if not skill_list:
		return []
	
	# Find users with matching skills
	users_with_skills = (
		db.query(User, Skill)
		.join(Skill, User.id == Skill.user_id)
		.filter(Skill.name.in_([s.capitalize() for s in skill_list]))
		.filter(User.id != current_user.id)  # Exclude current user
		.filter(User.profile_completed == True)  # Only completed profiles
		.all()
	)
	
	# Group by user and collect their skills
	user_skill_map = {}
	for user, skill in users_with_skills:
		if user.id not in user_skill_map:
			user_skill_map[user.id] = {
				"user_id": user.id,
				"name": user.name,
				"email": user.email,
				"skills": [],
			}
		user_skill_map[user.id]["skills"].append(skill.name)
	
	# Calculate match scores and sort
	results = []
	for user_data in user_skill_map.values():
		match_count = len(set(s.lower() for s in user_data["skills"]) & set(skill_list))
		results.append({
			**user_data,
			"match_score": match_count,
			"total_skills": len(user_data["skills"]),
		})
	
	# Sort by match score and return top results
	results.sort(key=lambda x: (x["match_score"], x["total_skills"]), reverse=True)
	return results[:limit]


@router.get("/search/by-interests")
def search_users_by_interests(
	interests: str,  # Comma-separated interests (using skills as proxy for now)
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	limit: int = 10,
):
	"""
	Search for users with similar interests.
	For now, uses skills as a proxy for interests.
	In future, can add a separate interests field.
	"""
	# Use skills as proxy for interests
	return search_users_by_skills(interests, current_user, db, limit)


@router.get("/search/by-email")
def search_user_by_email(
	email: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""
	Search for a user by email address.
	Useful for finding team members when you know their email.
	"""
	user = db.query(User).filter(User.email == email).filter(User.id != current_user.id).first()
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
	
	# Get user's skills
	user_skills = [skill.name for skill in db.query(Skill).filter(Skill.user_id == user.id)]
	
	return {
		"user_id": user.id,
		"name": user.name,
		"email": user.email,
		"skills": user_skills,
		"profile_completed": user.profile_completed,
	}


@router.get("/search/by-name")
def search_users_by_name(
	name: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	limit: int = 10,
):
	"""
	Search for users by name (partial match).
	Returns users whose names contain the search term.
	"""
	users = (
		db.query(User)
		.filter(User.name.ilike(f"%{name}%"))
		.filter(User.id != current_user.id)
		.filter(User.profile_completed == True)
		.limit(limit)
		.all()
	)
	
	results = []
	for user in users:
		user_skills = [skill.name for skill in db.query(Skill).filter(Skill.user_id == user.id)]
		results.append({
			"user_id": user.id,
			"name": user.name,
			"email": user.email,
			"skills": user_skills,
			"profile_completed": user.profile_completed,
		})
	
	return results
