from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import get_current_user
from ..models import Project, ChatMessage, UserStats, ModelPrediction
from ..schemas import AssistantChatRequest, AssistantChatResponse, PerformanceAnalysisResponse
from ..ai.assistant_chat_ai import generate_assistant_response
from ..ai.performance_ai import analyze_performance

router = APIRouter()


@router.post("/assistant-chat", response_model=AssistantChatResponse)
def assistant_chat(payload: AssistantChatRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
	# Allow project_id to be None for general AI assistance
	if payload.project_id:
		project = db.query(Project).filter(Project.id == payload.project_id).first()
		if not project:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
		
		recent_messages = (
			db.query(ChatMessage)
			.filter(ChatMessage.project_id == payload.project_id)
			.order_by(ChatMessage.created_at.desc())
			.limit(10)
			.all()
		)
		context = {
			"recent_messages": [msg.content for msg in recent_messages],
			"suggested_tasks": [
				"Review current milestone progress",
				"Pair with a teammate on blockers",
				"Update task board status",
			],
		}
	else:
		context = {
			"recent_messages": [],
			"suggested_tasks": [
				"Start a new project",
				"Update your profile",
				"Find team members",
			],
		}
	
	response = generate_assistant_response(payload.message, context)
	return AssistantChatResponse(response=response["response"], suggestions=response["suggestions"])


@router.post("/analyze-performance/{project_id}", response_model=PerformanceAnalysisResponse)
def analyze_project_performance(project_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
	project = db.query(Project).filter(Project.id == project_id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

	messages_count = db.query(ChatMessage).filter(ChatMessage.project_id == project_id).count()
	stats_entries = db.query(UserStats).all()
	reviews: List[Dict[str, Any]] = []
	for stats in stats_entries:
		reviews.extend(
			[
				{"rating": item.get("rating", 0)}
				for item in stats.reviews_received.get(project_id, [])
				if isinstance(stats.reviews_received, dict)
			]
		)

	result = analyze_performance(tasks_completed=5, messages_sent=messages_count, reviews=reviews, xp_base=100)

	model_log = ModelPrediction(
		project_id=project_id,
		model_name="performance_ai",
		input_json={"messages_count": messages_count},
		output_json=result,
		score=None,
	)
	db.add(model_log)
	db.commit()

	return PerformanceAnalysisResponse(**result)
