from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	secret_key: str = "change_me_development_secret"
	algorithm: str = "HS256"
	access_token_expire_minutes: int = 43200  # 30 days (30 * 24 * 60 = 43200 minutes)
	database_url: str = "sqlite:///./backend/app.db"
	env: str = "development"
	log_level: str = "INFO"
	# Note: ALLOW_ORIGINS is read directly from os.getenv in main.py, not from settings
	# This prevents Pydantic Settings from trying to parse it as JSON

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		case_sensitive=False,
		extra="ignore",
	)


class TokenData(BaseModel):
	sub: str


settings = Settings()


