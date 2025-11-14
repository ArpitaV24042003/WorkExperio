def calculate_level(xp_points: int) -> str:
	if xp_points < 500:
		return "bronze"
	if xp_points < 1500:
		return "silver"
	if xp_points < 3000:
		return "gold"
	return "platinum"

