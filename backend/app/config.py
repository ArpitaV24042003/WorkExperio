from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
	secret_key: str = "change_me_development_secret"
	algorithm: str = "HS256"
	access_token_expire_minutes: int = 60
	database_url: str = "sqlite:///./backend/app.db"
	env: str = "development"
	allow_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
	log_level: str = "INFO"

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		case_sensitive=False,
		extra="ignore",
	)


class TokenData(BaseModel):
	sub: str


settings = Settings()


