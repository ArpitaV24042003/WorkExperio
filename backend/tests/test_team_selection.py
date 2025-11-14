from app.ai.team_selection import recommend_team


def test_recommend_team_prioritizes_skill_matches():
	user_profiles = [
		{"user_id": "user-a", "skills": ["python", "fastapi", "sqlalchemy"]},
		{"user_id": "user-b", "skills": ["html", "css"]},
		{"user_id": "user-c", "skills": ["python", "react"]},
	]
	project_requirements = ["python", "fastapi"]

	result = recommend_team(user_profiles, project_requirements)

	assert result["recommended_team"][0] == "user-a"
	assert len(result["recommended_team"]) == 3

