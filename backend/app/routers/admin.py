from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Project, ProjectWaitlist

router = APIRouter()

AUTO_ASSIGN_DELAY = timedelta(days=7)


@router.post("/process-waitlists")
def process_waitlists(db: Session = Depends(get_db)):
	now = datetime.now(timezone.utc)
	processed = []
	waitlists = db.query(ProjectWaitlist).all()
	for entry in waitlists:
		if now - entry.created_at.replace(tzinfo=timezone.utc) >= AUTO_ASSIGN_DELAY:
			project = db.query(Project).filter(Project.id == entry.project_id).first()
			if project and project.team_type != "solo":
				project.team_type = "solo"
				project.team_id = None
				processed.append(project.id)
	db.commit()
	return {"processed_projects": processed, "count": len(processed)}

