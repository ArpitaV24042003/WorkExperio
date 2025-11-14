from __future__ import annotations

from typing import List, Dict, Any
from collections import Counter


def recommend_team(user_profiles: List[Dict[str, Any]], project_requirements: List[str]) -> Dict[str, Any]:
	"""
	Simple heuristic for team recommendation:
	- Count skill overlaps with project requirements.
	- Rank users by matches and diversity of skills.
	"""
	scores = []
	for profile in user_profiles:
		user_id = profile["user_id"]
		skills = profile.get("skills", [])
		match_count = len(set(skill.lower() for skill in skills) & set(req.lower() for req in project_requirements))
		diversity_score = len(set(skills))
		scores.append(
			{
				"user_id": user_id,
				"match_score": match_count,
				"diversity_score": diversity_score,
			}
		)

	sorted_users = sorted(scores, key=lambda item: (item["match_score"], item["diversity_score"]), reverse=True)
	selected = [user["user_id"] for user in sorted_users[: min(4, len(sorted_users))]]

	return {
		"recommended_team": selected,
		"scoring": sorted_users,
		"project_requirements": project_requirements,
	}

