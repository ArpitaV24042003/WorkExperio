def test_add_xp_updates_user_stats(test_client, current_user, db_session):
	response = test_client.post(f"/users/{current_user.id}/add-xp", json={"points": 120, "reason": "completed milestone"})
	assert response.status_code == 200
	data = response.json()
	assert data["total_xp"] == 120
	db_session.refresh(current_user.stats)
	assert current_user.stats.total_xp == 120

