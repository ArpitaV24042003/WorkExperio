from __future__ import annotations

from typing import Dict, Any, List


def analyze_performance(
	tasks_completed: int,
	messages_sent: int,
	reviews: List[Dict[str, Any]],
	xp_base: int,
	files_uploaded: int = 0,
) -> Dict[str, Any]:
	review_scores = [review.get("rating", 0) for review in reviews]
	avg_review = sum(review_scores) / len(review_scores) if review_scores else 0

	participation_score = min(1.0, messages_sent / 20) * 100
	task_consistency_score = min(1.0, tasks_completed / 10) * 100
	communication_score = min(1.0, messages_sent / 15) * 100
	# File uploads contribute to participation and task consistency
	files_contribution = min(1.0, files_uploaded / 5) * 100  # 5 files = 100% contribution
	
	# Adjust scores to include file uploads
	participation_score = min(100, participation_score + files_contribution * 0.3)
	task_consistency_score = min(100, task_consistency_score + files_contribution * 0.4)

	total_xp_awarded = int(xp_base + task_consistency_score * 0.5 + avg_review * 10 + files_uploaded * 2)

	return {
		"participation_score": round(participation_score, 2),
		"task_consistency_score": round(task_consistency_score, 2),
		"communication_score": round(communication_score, 2),
		"files_uploaded": files_uploaded,
		"files_contribution_score": round(files_contribution, 2),
		"review_summary": {
			"average_rating": round(avg_review, 2),
			"ratings": review_scores,
		},
		"total_xp_awarded": total_xp_awarded,
	}

