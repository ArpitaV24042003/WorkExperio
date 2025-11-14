from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import get_current_user
from ..models import User, UserStats
from ..schemas import XPUpdateRequest, ReviewRequest
from ..utils import calculate_level

router = APIRouter()


@router.post("/{user_id}/add-xp")
def add_xp(user_id: str, payload: XPUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	if current_user.id != user_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

	stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
	if not stats:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stats not found")

	stats.total_xp += payload.points
	stats.ai_score = max(stats.ai_score, payload.points / 10)

	user = db.query(User).filter(User.id == user_id).first()
	user.xp_points = stats.total_xp

	db.commit()
	return {
		"user_id": user_id,
		"total_xp": stats.total_xp,
		"level": calculate_level(stats.total_xp),
		"reason": payload.reason,
	}


@router.post("/{user_id}/reviews")
def submit_review(
	user_id: str,
	payload: ReviewRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	if current_user.id == user_id:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot review yourself")

	stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
	if not stats:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stats not found")

	reviews = stats.reviews_received or {}
	project_reviews = reviews.setdefault("general", [])
	project_reviews.append(
		{
			"reviewer_id": payload.reviewer_id,
			"rating": payload.rating,
			"comment": payload.comment,
		}
	)
	stats.reviews_received = reviews
	stats.total_xp += payload.rating * 10
	stats.ai_score = max(stats.ai_score, payload.rating * 12)

	user = db.query(User).filter(User.id == user_id).first()
	user.xp_points = stats.total_xp

	db.commit()

	return {
		"user_id": user_id,
		"reviews_received": stats.reviews_received,
		"total_xp": stats.total_xp,
		"level": calculate_level(stats.total_xp),
	}

