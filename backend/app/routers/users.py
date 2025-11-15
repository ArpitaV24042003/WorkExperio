from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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

	for entry in extracted.get("education", []):
		db.add(Education(user_id=user_id, institution=entry, degree="", field=""))
	for entry in extracted.get("experience", []):
		db.add(Experience(user_id=user_id, company=entry, role=entry, description="Imported from resume"))
	for entry in extracted.get("skills", []):
		db.add(Skill(user_id=user_id, name=entry))

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
