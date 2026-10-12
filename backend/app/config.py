import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "placeholder_app_secret"
    JWT_SECRET_KEY: str = "placeholder_jwt_secret"
    TOKEN_ENCRYPTION_KEY: str = "placeholder_token_encryption"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/digital_detox"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/callback"
    FRONTEND_URL: str = "http://localhost:5500"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
