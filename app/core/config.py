from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

class Settings(BaseSettings):
  PROJECT_NAME: str = "Fast API Backend"
  DEBUG: bool = False

  DATABASE_URL: str
  POSTGRES_USER: str
  POSTGRES_PASSWORD: str
  POSTGRES_DB: str

  REDIS_URL: str

  GOOGLE_CLIENT_SECRETS_FILE: str = "credentials/client_secret.json"
  GOOGLE_DRIVE_REDIRECT_URI: str = (
      "http://localhost:8000/google-drive/callback"
  )
  GOOGLE_DRIVE_SCOPES: List[str] = [
      "https://www.googleapis.com/auth/drive.file",
      "https://www.googleapis.com/auth/userinfo.email",
      "openid",
  ]
  GOOGLE_DRIVE_FOLDER_ID: Optional[str] = None
  GOOGLE_OAUTH_TOKEN_FILE: Optional[str] = "credentials/token.json"

  SECRET_KEY: str
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

  model_config = SettingsConfigDict(
      env_file=".env",
      env_file_encoding="utf-8",
      extra="ignore",
  )


@lru_cache
def get_settings() -> Settings:
  return Settings()


settings = get_settings()