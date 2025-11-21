from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..db import get_db
from ..dependencies import get_current_user
from ..models import (
	Project,
	User,
	Task,
	TimeLog,
	ProjectContribution,
	AIChatMessage,
	Team,
	TeamMember,
	ProjectFile,
	ChatMessage,
)
from ..schemas import (
	TaskCreate,
	TaskRead,
	TaskUpdate,
	TimeLogRead,
	ProjectAnalyticsOverview,
	MemberAnalytics,
	TimelinePoint,
	UserAnalyticsResponse,
	AIProjectChatRequest,
	AIProjectChatResponse,
	AIChatMessageRead,
	CodeQualityAnalysisResponse,
	AIAssignmentPlan,
	AIAssignedTask,
)
from ..ai.assistant_chat_ai import generate_assistant_response
from . import files as files_router


router = APIRouter()


def _validate_uuid(id_str: str, field_name: str = "id") -> None:
	"""Basic UUID v4 string validation (SQLite stores as text)."""
	if not isinstance(id_str, str) or len(id_str) != 36:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"Invalid {field_name}: expected UUID string",
		)


def _get_project_or_404(db: Session, project_id: str) -> Project:
	_validate_uuid(project_id, "project_id")
	project = db.query(Project).filter(Project.id == project_id).first()
	if not project:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
	return project


def _ensure_project_access(project: Project, current_user: User, db: Session) -> None:
	"""Allow access if user is owner or a team member."""
	if project.owner_id == current_user.id:
		return

	if not project.team_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this project")

	team = db.query(Team).filter(Team.id == project.team_id).first()
	if not team:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this project")

	member = (
		db.query(TeamMember)
		.filter(TeamMember.team_id == team.id, TeamMember.user_id == current_user.id)
		.first()
	)
	if not member:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this project")


def _get_or_create_contribution(db: Session, project_id: str, user_id: str) -> ProjectContribution:
	contrib = (
		db.query(ProjectContribution)
		.filter(ProjectContribution.project_id == project_id, ProjectContribution.user_id == user_id)
		.first()
	)
	if not contrib:
		contrib = ProjectContribution(project_id=project_id, user_id=user_id)
		db.add(contrib)
		db.flush()
	return contrib


def _compute_member_skill_vector(db: Session, user_id: str) -> List[str]:
	"""
	Simple capability vector for a member derived from Skill rows.
	We deliberately keep this deterministic and lightweight (no LLM call).
	"""
	from ..models import Skill  # local import to avoid circulars

	skills = db.query(Skill).filter(Skill.user_id == user_id).all()
	return [s.name.lower() for s in skills]


def _task_fit_score(
	task_title: str,
	task_description: Optional[str],
	member_skills: List[str],
	current_load_hours: float,
	estimated_hours: float,
) -> Tuple[float, float, float, float]:
	"""
	Deterministic scoring function from the spec:

	fit_score(member, task) = α * skill_match + β * availability + γ * past_performance

	Here we approximate:
	- skill_match in [0,100] from keyword overlap
	- availability in [0,1] from current workload vs. estimated_hours
	- past_performance is proxied via low current_load_hours
	"""
	text = f"{task_title} {task_description or ''}".lower()

	# Skill match: fraction of member skills that appear as substrings in the task text
	if member_skills:
		match_count = sum(1 for s in member_skills if s and s in text)
		skill_match = (match_count / len(member_skills)) * 100.0
	else:
		skill_match = 0.0

	# Availability: prefer members with less current load; clamp to [0,1]
	# Assume that up to 40h of assigned work is "full".
	max_hours = 40.0
	availability = max(0.0, 1.0 - min(current_load_hours, max_hours) / max_hours)

	# Past performance proxy: again, lower current load gets higher score.
	past_performance = max(0.0, 1.0 - min(current_load_hours, max_hours) / max_hours)

	alpha, beta, gamma = 0.5, 0.3, 0.2
	fit_score = alpha * skill_match + beta * availability * 100.0 + gamma * past_performance * 100.0

	# Workload penalty (for debugging / UI only)
	workload_penalty = (current_load_hours / max_hours) * 100.0

	return fit_score, skill_match, availability, workload_penalty


@router.post("/projects/{project_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
	project_id: str,
	payload: TaskCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	project = _get_project_or_404(db, project_id)
	_ensure_project_access(project, current_user, db)

	task = Task(
		project_id=project.id,
		title=payload.title,
		description=payload.description,
		assignee_id=payload.assignee_id,
		estimated_hours=payload.estimated_hours,
		status=payload.status or "todo",
		due_date=payload.due_date,
	)
	db.add(task)
	db.commit()
	db.refresh(task)
	return TaskRead.model_validate(task)


@router.get("/projects/{project_id}/tasks", response_model=List[TaskRead])
def list_tasks(
	project_id: str,
	status_filter: Optional[str] = None,
	assignee_id: Optional[str] = None,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	project = _get_project_or_404(db, project_id)
	_ensure_project_access(project, current_user, db)

	query = db.query(Task).filter(Task.project_id == project.id)
	if status_filter:
		query = query.filter(Task.status == status_filter)
	if assignee_id:
		query = query.filter(Task.assignee_id == assignee_id)

	tasks = query.order_by(Task.created_at.asc()).all()
	return [TaskRead.model_validate(t) for t in tasks]


@router.patch("/projects/{project_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(
	project_id: str,
	task_id: str,
	payload: TaskUpdate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	project = _get_project_or_404(db, project_id)
	_ensure_project_access(project, current_user, db)
	_validate_uuid(task_id, "task_id")

	task = db.query(Task).filter(Task.id == task_id, Task.project_id == project.id).first()
	if not task:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

	previous_status = task.status

	for field, value in payload.model_dump(exclude_unset=True).items():
		setattr(task, field, value)

	# Track completion time and contribution when moving to done
	if previous_status != "done" and task.status == "done":
		task.completed_at = datetime.now(timezone.utc)
		if task.assignee_id:
			contrib = _get_or_create_contribution(db, project.id, task.assignee_id)
			contrib.tasks_completed += 1

	db.commit()
	db.refresh(task)
	return TaskRead.model_validate(task)


@router.post("/tasks/{task_id}/timelogs/start", response_model=TimeLogRead, status_code=status.HTTP_201_CREATED)
def start_timelog(
	task_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	_validate_uuid(task_id, "task_id")
	task = db.query(Task).filter(Task.id == task_id).first()
	if not task:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

	project = _get_project_or_404(db, task.project_id)
	_ensure_project_access(project, current_user, db)

	# Prevent multiple open timers for the same user & task
	open_log = (
		db.query(TimeLog)
		.filter(
			TimeLog.task_id == task.id,
			TimeLog.user_id == current_user.id,
			TimeLog.end_time.is_(None),
		)
		.first()
	)
	if open_log:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="There is already an active timer for this task",
		)

	log = TimeLog(task_id=task.id, user_id=current_user.id)
	db.add(log)
	db.commit()
	db.refresh(log)
	return TimeLogRead.model_validate(log)


@router.post("/tasks/{task_id}/timelogs/stop", response_model=TimeLogRead)
def stop_timelog(
	task_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	_validate_uuid(task_id, "task_id")
	task = db.query(Task).filter(Task.id == task_id).first()
	if not task:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

	project = _get_project_or_404(db, task.project_id)
	_ensure_project_access(project, current_user, db)

	log = (
		db.query(TimeLog)
		.filter(
			TimeLog.task_id == task.id,
			TimeLog.user_id == current_user.id,
			TimeLog.end_time.is_(None),
		)
		.order_by(TimeLog.start_time.desc())
		.first()
	)
	if not log:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active timer found for this task")

	now = datetime.now(timezone.utc)
	log.end_time = now
	if log.start_time:
		duration_minutes = int((now - log.start_time).total_seconds() / 60)
		log.duration_minutes = max(duration_minutes, 0)

		# Update contribution in hours
		contrib = _get_or_create_contribution(db, project.id, current_user.id)
		contrib.total_hours += (log.duration_minutes or 0) / 60.0

	db.commit()
	db.refresh(log)
	return TimeLogRead.model_validate(log)


@router.get("/projects/{project_id}/analytics/overview", response_model=ProjectAnalyticsOverview)
def project_analytics_overview(
	project_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	project = _get_project_or_404(db, project_id)
	_ensure_project_access(project, current_user, db)

	# Task level metrics
	tasks = db.query(Task).filter(Task.project_id == project.id).all()
	total_tasks = len(tasks)
	completed_tasks = [t for t in tasks if t.status == "done"]
	tasks_completed = len(completed_tasks)
	percent_complete = (tasks_completed / total_tasks * 100.0) if total_tasks else 0.0

	# Overdue tasks
	now = datetime.now(timezone.utc)
	overdue_tasks = [
		t
		for t in tasks
		if t.due_date is not None and t.status != "done" and t.due_date.replace(tzinfo=timezone.utc) < now
	]

	# Timeline: daily completed tasks counts
	timeline_counts: Dict[str, int] = defaultdict(int)
	for t in completed_tasks:
		if t.completed_at:
			day = t.completed_at.date().isoformat()
		else:
			day = project.created_at.date().isoformat()
		timeline_counts[day] += 1
	timeline = [
		TimelinePoint(date=day, completed_count=count)
		for day, count in sorted(timeline_counts.items())
	]

	# Per-member contributions and raw activity
	contribs = db.query(ProjectContribution).filter(ProjectContribution.project_id == project.id).all()
	contrib_by_user = {c.user_id: c for c in contribs}

	# Files per user
	files_per_user: Dict[str, int] = defaultdict(int)
	for f in db.query(ProjectFile).filter(ProjectFile.project_id == project.id).all():
		files_per_user[f.user_id] += 1

	# Messages per user
	messages_per_user: Dict[str, int] = defaultdict(int)
	for m in db.query(ChatMessage).filter(ChatMessage.project_id == project.id).all():
		messages_per_user[m.user_id] += 1

	# AI interactions per user
	ai_per_user: Dict[str, int] = defaultdict(int)
	for m in db.query(AIChatMessage).filter(AIChatMessage.project_id == project.id, AIChatMessage.role == "user").all():
		if m.user_id:
			ai_per_user[m.user_id] += 1

	# Timeliness per user and project-level on-time / delay rates.
	on_time_counts: Dict[str, int] = defaultdict(int)
	late_counts: Dict[str, int] = defaultdict(int)
	due_counts: Dict[str, int] = defaultdict(int)
	for t in completed_tasks:
		if not t.assignee_id or not t.due_date or not t.completed_at:
			continue
		due_counts[t.assignee_id] += 1
		if t.completed_at <= t.due_date:
			on_time_counts[t.assignee_id] += 1
		else:
			late_counts[t.assignee_id] += 1

	total_completed_with_due = sum(due_counts.values())
	total_on_time = sum(on_time_counts.values())
	total_late = sum(late_counts.values())
	on_time_rate = (total_on_time / total_completed_with_due) if total_completed_with_due else 0.0
	delay_rate = (total_late / total_completed_with_due) if total_completed_with_due else 0.0

	members: List[MemberAnalytics] = []
	total_member_hours = 0.0
	total_files_uploaded = 0
	total_messages = 0
	total_ai_interactions = 0

	# Participation normalization baseline so scores end up roughly in 0–100
	max_messages = max(messages_per_user.values()) if messages_per_user else 0
	max_files = max(files_per_user.values()) if files_per_user else 0
	max_ai = max(ai_per_user.values()) if ai_per_user else 0

	for user_id, contrib in contrib_by_user.items():
		tasks_done = contrib.tasks_completed
		total_hours = contrib.total_hours
		code_quality = contrib.code_quality_score
		files_uploaded = files_per_user.get(user_id, 0)
		messages_sent = messages_per_user.get(user_id, 0)
		ai_interactions = ai_per_user.get(user_id, 0)

		# --- Contribution Score (0–100) ---
		# Spec formula:
		#   tasks_component = (member_tasks_done / total_tasks_done) * 0.5
		#   files_component = (member_files_uploaded / total_files_uploaded) * 0.3
		#   comm_component  = (member_messages / total_messages) * 0.2
		#   contribution_score = (tasks_component + files_component + comm_component) * 100
		tasks_den = tasks_completed or 1
		files_den = total_files_uploaded or 1
		messages_den = total_messages or 1

		tasks_component = (tasks_done / tasks_den) * 0.5
		files_component = (files_uploaded / files_den) * 0.3
		comm_component = (messages_sent / messages_den) * 0.2
		contribution_score = (tasks_component + files_component + comm_component) * 100.0

		# Task consistency as on-time completion % (0–100)
		due = due_counts.get(user_id, 0)
		on_time = on_time_counts.get(user_id, 0)
		task_consistency_score = (on_time / due * 100.0) if due else 0.0

		# Participation score (0–100) based on messages, files, AI interactions.
		# We normalize each dimension independently and average them.
		parts: List[float] = []
		if max_messages:
			parts.append((messages_sent / max_messages) * 100.0)
		if max_files:
			parts.append((files_uploaded / max_files) * 100.0)
		if max_ai:
			parts.append((ai_interactions / max_ai) * 100.0)
		participation_score = sum(parts) / len(parts) if parts else 0.0

		# Simple communication score heuristic: more, longer messages score higher
		user_msgs = db.query(ChatMessage).filter(ChatMessage.project_id == project.id, ChatMessage.user_id == user_id).all()
		if user_msgs:
			avg_len = sum(len(m.content or "") for m in user_msgs) / len(user_msgs)
			communication_score = min(100.0, (len(user_msgs) * 3.0) + (avg_len / 10.0))
		else:
			communication_score = 0.0

		members.append(
			MemberAnalytics(
				user_id=user_id,
				tasks_completed=tasks_done,
				total_hours=total_hours,
				code_quality_score=code_quality,
				project_id=project.id,
				contribution_score=contribution_score,
				task_consistency_score=task_consistency_score,
				participation_score=participation_score,
				communication_score=communication_score,
				files_uploaded=files_uploaded,
				messages_sent=messages_sent,
				ai_interactions=ai_interactions,
			)
		)

		total_member_hours += total_hours
		total_files_uploaded += files_uploaded
		total_messages += messages_sent
		total_ai_interactions += ai_interactions

	# Simple average completion time from timelogs
	durations = (
		db.query(TimeLog.duration_minutes)
		.join(Task, Task.id == TimeLog.task_id)
		.filter(Task.project_id == project.id, TimeLog.duration_minutes.isnot(None))
		.all()
	)
	if durations:
		total_minutes = sum(d[0] for d in durations if d[0] is not None)
		avg_completion_minutes = total_minutes / len(durations)
	else:
		avg_completion_minutes = 0.0

	avg_code_quality = 0.0
	if contribs:
		avg_code_quality = sum(c.code_quality_score for c in contribs) / len(contribs)

	# --- Team Performance Score (0–100) ---
	# team_score = 0.4*avg_code_quality + 0.35*on_time_rate*100 + 0.25*participation_score
	avg_participation = 0.0
	if members:
		avg_participation = sum(m.participation_score for m in members) / len(members)
	team_participation_score = avg_participation
	team_performance_score = (
		0.4 * avg_code_quality + 0.35 * on_time_rate * 100.0 + 0.25 * team_participation_score
	)

	return ProjectAnalyticsOverview(
		project_id=project.id,
		total_tasks=total_tasks,
		tasks_completed=tasks_completed,
		percent_complete=percent_complete,
		overdue_tasks=len(overdue_tasks),
		members=members,
		timeline=timeline,
		avg_completion_minutes=avg_completion_minutes,
		code_quality_average=avg_code_quality,
		total_member_hours=total_member_hours,
		total_files_uploaded=total_files_uploaded,
		total_messages=total_messages,
		total_ai_interactions=total_ai_interactions,
		on_time_rate=on_time_rate,
		delay_rate=delay_rate,
		team_participation_score=team_participation_score,
		team_performance_score=team_performance_score,
	)


@router.get("/users/{user_id}/analytics", response_model=UserAnalyticsResponse)
def user_analytics(
	user_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	_validate_uuid(user_id, "user_id")
	if current_user.id != user_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

	contribs = db.query(ProjectContribution).filter(ProjectContribution.user_id == user_id).all()

	per_project: List[MemberAnalytics] = []
	for c in contribs:
		per_project.append(
			MemberAnalytics(
				user_id=user_id,
				tasks_completed=c.tasks_completed,
				total_hours=c.total_hours,
				code_quality_score=c.code_quality_score,
				project_id=c.project_id,
			)
		)

	# Global KPIs
	all_logs = (
		db.query(TimeLog)
		.join(Task, Task.id == TimeLog.task_id)
		.filter(TimeLog.user_id == user_id, TimeLog.duration_minutes.is_not(None))
		.all()
	)
	if all_logs:
		total_minutes = sum(l.duration_minutes or 0 for l in all_logs)
		avg_completion_minutes = total_minutes / len(all_logs)
	else:
		avg_completion_minutes = 0.0

	# On-time completion: tasks with due_date and completed before due_date
	task_q = (
		db.query(Task)
		.join(TimeLog, Task.id == TimeLog.task_id)
		.filter(Task.assignee_id == user_id, Task.status == "done")
	)
	user_tasks = task_q.all()
	on_time = 0
	on_time_denominator = 0
	for t in user_tasks:
		if t.due_date and t.completed_at:
			on_time_denominator += 1
			if t.completed_at <= t.due_date:
				on_time += 1
	on_time_ratio = (on_time / on_time_denominator) if on_time_denominator else 0.0

	avg_code_quality = 0.0
	if contribs:
		avg_code_quality = sum(c.code_quality_score for c in contribs) / len(contribs)

	return UserAnalyticsResponse(
		user_id=user_id,
		projects=per_project,
		avg_completion_minutes=avg_completion_minutes,
		on_time_completion_ratio=on_time_ratio,
		code_quality_average=avg_code_quality,
	)


@router.post("/projects/{project_id}/ai/chat", response_model=AIProjectChatResponse)
def project_ai_chat(
	project_id: str,
	payload: AIProjectChatRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	project = _get_project_or_404(db, project_id)
	_ensure_project_access(project, current_user, db)

	# Persist user message
	user_msg = AIChatMessage(
		project_id=project.id,
		user_id=current_user.id,
		role="user",
		content=payload.message,
	)
	db.add(user_msg)
	db.flush()

	# Load recent history for context
	history_rows = (
		db.query(AIChatMessage)
		.filter(AIChatMessage.project_id == project.id)
		.order_by(AIChatMessage.created_at.desc())
		.limit(20)
		.all()
	)
	conversation_history = [
		{"role": row.role, "content": row.content} for row in reversed(history_rows)
	]

	# Build richer project context for higher quality answers
	project_tasks = db.query(Task).filter(Task.project_id == project.id).all()
	project_files = db.query(ProjectFile).filter(ProjectFile.project_id == project.id).all()
	team_members: List[TeamMember] = []
	if project.team_id:
		team_members = db.query(TeamMember).filter(TeamMember.team_id == project.team_id).all()

	context: Dict[str, Any] = {
		"project_title": project.title,
		"project_description": project.description,
		"conversation_history": conversation_history,
		"tasks": [
			{
				"id": t.id,
				"title": t.title,
				"status": t.status,
				"assignee_id": t.assignee_id,
				"due_date": t.due_date.isoformat() if t.due_date else None,
			}
			for t in project_tasks
		],
		"team_members": [
			{
				"user_id": m.user_id,
				"role": m.role,
			}
			for m in team_members
		],
		"files": [
			{
				"id": f.id,
				"filename": f.filename,
				"file_type": f.file_type,
			}
			for f in project_files
		],
		"suggested_tasks": [
			"Review open tasks and pick the next one",
			"Check overdue tasks and re-prioritize",
			"Summarize the current project status for the team",
		],
	}

	# Deterministic, local assistant fallback (no external API required)
	response_payload = generate_assistant_response(payload.message, context, conversation_history)
	reply_text = response_payload["response"]

	assistant_msg = AIChatMessage(
		project_id=project.id,
		user_id=None,
		role="assistant",
		content=reply_text,
	)
	db.add(assistant_msg)
	db.commit()
	db.refresh(assistant_msg)

	return AIProjectChatResponse(reply=reply_text, id=assistant_msg.id)


@router.get("/projects/{project_id}/ai/history", response_model=List[AIChatMessageRead])
def project_ai_history(
	project_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	limit: int = 50,
):
	project = _get_project_or_404(db, project_id)
	_ensure_project_access(project, current_user, db)

	messages = (
		db.query(AIChatMessage)
		.filter(AIChatMessage.project_id == project.id)
		.order_by(AIChatMessage.created_at.asc())
		.limit(limit)
		.all()
	)
	return [AIChatMessageRead.model_validate(m) for m in messages]


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
	project_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	import os
	import shutil
	from pathlib import Path

	project = _get_project_or_404(db, project_id)
	if project.owner_id != current_user.id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can delete the project")

	# Delete DB row (cascades should handle related rows where configured)
	db.delete(project)
	db.commit()

	# Clean up uploaded files from disk (best-effort)
	base_upload_dir = Path("backend/uploads/projects")
	project_dir = base_upload_dir / project_id
	if project_dir.exists():
		shutil.rmtree(project_dir, ignore_errors=True)

	return None


@router.post("/projects/{project_id}/files", response_model=Dict[str, Any])
async def upload_project_file_via_projects(
	project_id: str,
	file: UploadFile = File(...),
	description: Optional[str] = Form(None),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""
	Thin wrapper over the existing /files/projects/{project_id}/upload endpoint so that
	the dashboard can call a more natural /projects/{id}/files route.
	"""
	# Reuse the implementation from files router
	response = await files_router.upload_project_file(
		project_id=project_id,
		file=file,
		description=description,
		current_user=current_user,
		db=db,
	)
	# Pydantic response model is already applied in files router; here we just pass through.
	return {
		"id": response.id,
		"filename": response.filename,
		"file_size": response.file_size,
		"uploaded_at": response.uploaded_at,
		"message": response.message,
	}


@router.get("/projects/{project_id}/files", response_model=List[Dict[str, Any]])
def list_project_files_via_projects(
	project_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	files = files_router.list_project_files(project_id=project_id, current_user=current_user, db=db)
	# list_project_files already returns Pydantic models; convert them to dicts for the dashboard
	return [f.model_dump() for f in files]


@router.get("/projects/{project_id}/members", response_model=Dict[str, Any])
def get_project_members(
	project_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	project = _get_project_or_404(db, project_id)
	_ensure_project_access(project, current_user, db)

	if not project.team_id:
		return {"project_id": project_id, "members": []}

	team = db.query(Team).filter(Team.id == project.team_id).first()
	members = db.query(TeamMember).filter(TeamMember.team_id == team.id).all()
	return {
		"project_id": project_id,
		"team_id": team.id,
		"members": [
			{
				"id": m.id,
				"user_id": m.user_id,
				"role": m.role,
				"task": m.task,
				"joined_at": m.joined_at,
			}
			for m in members
		],
	}


@router.post("/projects/{project_id}/members", response_model=Dict[str, Any])
def add_project_member(
	project_id: str,
	payload: Dict[str, str],
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""
	Add a known member to the project's team by user_id (UUID string).
	Only the project owner can add members.
	"""
	project = _get_project_or_404(db, project_id)
	if project.owner_id != current_user.id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can add members")

	user_id = payload.get("user_id")
	if not user_id:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id is required")
	_validate_uuid(user_id, "user_id")

	# Ensure user exists
	user = db.query(User).filter(User.id == user_id).first()
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

	# Ensure team exists
	team = None
	if project.team_id:
		team = db.query(Team).filter(Team.id == project.team_id).first()
	if not team:
		team = Team(project_id=project.id)
		db.add(team)
		db.flush()
		project.team_id = team.id
		project.team_type = "team"

	# Avoid duplicates
	existing_member = (
		db.query(TeamMember)
		.filter(TeamMember.team_id == team.id, TeamMember.user_id == user_id)
		.first()
	)
	if existing_member:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a project member")

	member = TeamMember(team_id=team.id, user_id=user_id, role=payload.get("role") or None)
	db.add(member)
	db.commit()
	db.refresh(member)

	return {
		"message": "Member added",
		"member": {
			"id": member.id,
			"user_id": member.user_id,
			"role": member.role,
			"task": member.task,
			"joined_at": member.joined_at,
		},
	}


@router.patch("/projects/{project_id}/members/{user_id}/role")
def update_project_member_role(
	project_id: str,
	user_id: str,
	payload: Dict[str, str],
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""
	Update a team member's role from the projects router.
	Reuses the same business rules as in the teams router:
	- Members can update their own role
	- Owners can update any member's role
	"""
	project = _get_project_or_404(db, project_id)
	if not project.team_id:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not assigned")

	team = db.query(Team).filter(Team.id == project.team_id).first()
	if not team:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

	member = (
		db.query(TeamMember)
		.filter(TeamMember.team_id == team.id, TeamMember.user_id == user_id)
		.first()
	)
	if not member:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found")

	# Authorization: self-update or owner
	if user_id != current_user.id and project.owner_id != current_user.id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own role")

	role = (payload.get("role") or "").strip()
	if not role:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role cannot be empty")

	member.role = role
	db.commit()
	db.refresh(member)

	return {
		"message": "Role updated successfully",
		"member": {
			"id": member.id,
			"user_id": member.user_id,
			"role": member.role,
			"task": member.task,
			"joined_at": member.joined_at,
		},
	}


@router.post("/projects/{project_id}/analyze-code", response_model=CodeQualityAnalysisResponse)
async def analyze_code_quality(
	project_id: str,
	file: UploadFile = File(...),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""
	Placeholder code-quality analysis endpoint.

	If radon is available it could be used here, but to keep the environment
	lightweight we compute a simple heuristic score from file length.
	"""
	project = _get_project_or_404(db, project_id)
	_ensure_project_access(project, current_user, db)

	content_bytes = await file.read()
	try:
		text = content_bytes.decode("utf-8", errors="ignore")
	except Exception:  # pragma: no cover - very defensive
		text = ""

	lines = text.splitlines()
	line_count = len(lines)
	char_count = len(text)

	# Very simple heuristic: shorter, focused files get higher scores
	if line_count == 0:
		score = 50.0
	else:
		base = 100.0
		penalty = min(50.0, line_count * 0.3)  # up to -50 points for very long files
		score = max(0.0, base - penalty)

	# Update ProjectContribution for the current user
	contrib = _get_or_create_contribution(db, project.id, current_user.id)
	contrib.code_quality_score = score
	db.commit()

	return CodeQualityAnalysisResponse(
		score=score,
		details={
			"line_count": line_count,
			"char_count": char_count,
			"project_id": project.id,
			"user_id": current_user.id,
		},
	)


@router.post("/projects/{project_id}/ai-assign", response_model=AIAssignmentPlan)
def ai_assign_tasks_and_schedule(
	project_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""
	Assign open tasks to team members using a deterministic scoring function.

	Fit score formula (as described in the spec):
	  fit_score(member, task) = α * skill_match + β * availability + γ * past_performance

	Where:
	  - skill_match is computed from resume/skill keywords vs. task text (0–100)
	  - availability is based on current assigned workload (0–1)
	  - past_performance is approximated by low current workload (0–1)

	The endpoint updates Task.assignee_id, Task.estimated_hours, and Task.due_date,
	and returns a structured plan that the UI can display.
	"""
	project = _get_project_or_404(db, project_id)
	if project.owner_id != current_user.id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Only the project owner can run AI assignment",
		)

	# Ensure there is a team with members
	if not project.team_id:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Team is not set for this project; create a team and add members first.",
		)

	team = db.query(Team).filter(Team.id == project.team_id).first()
	if not team:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

	members = db.query(TeamMember).filter(TeamMember.team_id == team.id).all()
	if not members:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="No team members available for assignment.",
		)

	# Precompute member skill vectors and current workload from existing tasks.
	member_skills: Dict[str, List[str]] = {}
	member_hours: Dict[str, float] = defaultdict(float)
	for m in members:
		member_skills[m.user_id] = _compute_member_skill_vector(db, m.user_id)

	existing_tasks = db.query(Task).filter(Task.project_id == project.id).all()
	for t in existing_tasks:
		if t.assignee_id and t.estimated_hours:
			member_hours[t.assignee_id] += float(t.estimated_hours)

	# Consider only tasks that are not yet completed.
	open_tasks = [t for t in existing_tasks if t.status != "done"]
	if not open_tasks:
		return AIAssignmentPlan(project_id=project.id, assignments=[], rationale=["No open tasks to assign."])

	assignments: List[AIAssignedTask] = []
	rationale: List[str] = []

	# Start scheduling from "now", allocate due dates based on estimated_hours.
	now = datetime.now(timezone.utc)
	hours_per_day = 4.0  # simple heuristic: 4 focused hours per day

	for task in open_tasks:
		best_member_id: Optional[str] = None
		best_fit: float = -1.0
		best_components: Tuple[float, float, float, float] | None = None

		est_hours = float(task.estimated_hours or 2.0)

		for m in members:
			user_id = m.user_id
			skills = member_skills.get(user_id, [])
			load_hours = member_hours.get(user_id, 0.0)

			fit, skill_match, availability, workload_penalty = _task_fit_score(
				task.title, task.description, skills, load_hours, est_hours
			)

			if fit > best_fit:
				best_fit = fit
				best_member_id = user_id
				best_components = (skill_match, availability, workload_penalty, fit)

		if not best_member_id or not best_components:
			continue

		skill_match, availability, workload_penalty, fit_score_val = best_components

		# Update task with chosen assignee and schedule
		task.assignee_id = best_member_id
		# Keep estimated_hours if already set; otherwise use est_hours
		if task.estimated_hours is None:
			task.estimated_hours = est_hours
		# Simple due date: today + ceil(estimated_hours / hours_per_day) days
		days_needed = max(1, int((float(task.estimated_hours) or est_hours) / hours_per_day + 0.5))
		task.due_date = now + timedelta(days=days_needed)

		# Update workload for future tasks
		member_hours[best_member_id] += float(task.estimated_hours or est_hours)

		assignments.append(
			AIAssignedTask(
				task_id=task.id,
				task_title=task.title,
				assignee_id=best_member_id,
				assignee_score=fit_score_val,
				skill_match=skill_match,
				availability=availability,
				workload_penalty=workload_penalty,
				estimated_hours=float(task.estimated_hours or est_hours),
				due_date=task.due_date,
			)
		)

		rationale.append(
			f"Assigned '{task.title}' to member {best_member_id} with fit score {fit_score_val:.1f} "
			f"(skill_match={skill_match:.1f}, availability={availability:.2f}, workload_penalty={workload_penalty:.1f})."
		)

	db.commit()

	return AIAssignmentPlan(project_id=project.id, assignments=assignments, rationale=rationale)



