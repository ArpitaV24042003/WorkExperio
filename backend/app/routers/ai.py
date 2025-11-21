from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import get_current_user
from ..models import Project, ChatMessage, UserStats, ModelPrediction, AIConversation
from ..schemas import AssistantChatRequest, AssistantChatResponse, PerformanceAnalysisResponse, AIConversationRead
from ..ai.assistant_chat_ai import generate_assistant_response
from ..ai.performance_ai import analyze_performance

router = APIRouter()


@router.get("/assistant-conversation")
def get_conversation_history(
	project_id: str = None,
	current_user=Depends(get_current_user),
	db: Session = Depends(get_db),
	limit: int = 50,
):
	"""Get AI conversation history for the current user and optional project"""
	query = db.query(AIConversation).filter(AIConversation.user_id == current_user.id)
	
	if project_id:
		query = query.filter(AIConversation.project_id == project_id)
	else:
		query = query.filter(AIConversation.project_id == None)
	
	conversations = query.order_by(AIConversation.created_at.asc()).limit(limit).all()
	return [AIConversationRead.model_validate(conv) for conv in conversations]


@router.post("/assistant-chat", response_model=AssistantChatResponse)
def assistant_chat(payload: AssistantChatRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
	# Allow project_id to be None for general AI assistance
	if payload.project_id:
		project = db.query(Project).filter(Project.id == payload.project_id).first()
		if not project:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
	
	# Get conversation history from database if not provided
	conversation_history = payload.conversation_history or []
	if not conversation_history:
		# Load from database
		query = db.query(AIConversation).filter(AIConversation.user_id == current_user.id)
		if payload.project_id:
			query = query.filter(AIConversation.project_id == payload.project_id)
		else:
			query = query.filter(AIConversation.project_id == None)
		
		prev_conversations = query.order_by(AIConversation.created_at.desc()).limit(20).all()
		conversation_history = [
			{"role": conv.role, "content": conv.content}
			for conv in reversed(prev_conversations)
		]
	
	# Add current user message to history
	conversation_history.append({"role": "user", "content": payload.message})
	
	# Store user message in database
	user_message = AIConversation(
		user_id=current_user.id,
		project_id=payload.project_id,
		role="user",
		content=payload.message,
	)
	db.add(user_message)
	db.flush()
	
	# Prepare context with conversation history
	if payload.project_id:
		recent_team_messages = (
			db.query(ChatMessage)
			.filter(ChatMessage.project_id == payload.project_id)
			.order_by(ChatMessage.created_at.desc())
			.limit(5)
			.all()
		)
		context = {
			"conversation_history": conversation_history,
			"recent_team_messages": [msg.content for msg in recent_team_messages],
			"suggested_tasks": [
				"Review current milestone progress",
				"Pair with a teammate on blockers",
				"Update task board status",
			],
		}
	else:
		context = {
			"conversation_history": conversation_history,
			"recent_team_messages": [],
			"suggested_tasks": [
				"Start a new project",
				"Update your profile",
				"Find team members",
			],
		}
	
	# Generate response with full conversation context
	response = generate_assistant_response(payload.message, context, conversation_history)
	
	# Store assistant response in database
	assistant_message = AIConversation(
		user_id=current_user.id,
		project_id=payload.project_id,
		role="assistant",
		content=response["response"],
	)
	db.add(assistant_message)
	db.commit()
	
	return AssistantChatResponse(
		response=response["response"],
		suggestions=response["suggestions"],
		conversation_id=str(user_message.id),  # Use user message ID as conversation identifier
	)


@router.post("/analyze-performance/{project_id}", response_model=PerformanceAnalysisResponse)
def analyze_project_performance(project_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
	from ..models import ProjectFile
	
	project = db.query(Project).filter(Project.id == project_id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

	messages_count = db.query(ChatMessage).filter(ChatMessage.project_id == project_id).count()
	
	# Get files uploaded for this project by current user
	files_uploaded = db.query(ProjectFile).filter(
		ProjectFile.project_id == project_id,
		ProjectFile.user_id == current_user.id
	).count()
	
	# Get images/pictures uploaded for this project by current user (for reports)
	images_uploaded = db.query(ProjectFile).filter(
		ProjectFile.project_id == project_id,
		ProjectFile.user_id == current_user.id,
		ProjectFile.file_type == "image"
	).all()
	
	# Get all project files (for report display)
	all_project_files = db.query(ProjectFile).filter(
		ProjectFile.project_id == project_id
	).all()
	
	# Get user stats for reviews
	user_stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()
	reviews: List[Dict[str, Any]] = []
	if user_stats and isinstance(user_stats.reviews_received, dict):
		reviews.extend(
			[
				{"rating": item.get("rating", 0)}
				for item in user_stats.reviews_received.get(project_id, [])
			]
		)
	
	# Get tasks completed from user stats
	tasks_completed = user_stats.tasks_completed if user_stats else 0

	result = analyze_performance(
		tasks_completed=tasks_completed,
		messages_sent=messages_count,
		reviews=reviews,
		xp_base=100,
		files_uploaded=files_uploaded
	)
	
	# Add image data to result for report display
	result["images_count"] = len(images_uploaded)
	result["images"] = [
		{
			"id": img.id,
			"filename": img.filename,
			"file_path": img.file_path,
			"mime_type": img.mime_type,
			"uploaded_at": img.uploaded_at.isoformat() if img.uploaded_at else None
		}
		for img in images_uploaded
	]
	
	# Add all files summary
	result["all_files"] = [
		{
			"id": f.id,
			"filename": f.filename,
			"file_type": f.file_type,
			"file_size": f.file_size,
			"uploaded_at": f.uploaded_at.isoformat() if f.uploaded_at else None
		}
		for f in all_project_files
	]

	model_log = ModelPrediction(
		project_id=project_id,
		model_name="performance_ai",
		input_json={"messages_count": messages_count, "files_uploaded": files_uploaded, "tasks_completed": tasks_completed},
		output_json=result,
		score=None,
	)
	db.add(model_log)
	db.commit()

	return PerformanceAnalysisResponse(**result)
