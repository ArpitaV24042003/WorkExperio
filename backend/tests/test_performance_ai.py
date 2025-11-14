from app.models import Project


def test_performance_analysis_endpoint(test_client, db_session, current_user):
	project = Project(
		title="Test Project",
		description="Testing performance analysis",
		owner_id=current_user.id,
	)
	db_session.add(project)
	db_session.commit()

	response = test_client.post(f"/ai/analyze-performance/{project.id}")
	assert response.status_code == 200
	data = response.json()
	assert "participation_score" in data
	assert "total_xp_awarded" in data

