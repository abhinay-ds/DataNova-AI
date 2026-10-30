from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):

    GROQ_API_KEY: str = ""
    JWT_SECRET_KEY: str = "datanova-auth-secret-key-prod-9a7c8b2e1f40"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    DATABASE_URL: str = ""
    ENVIRONMENT: str = "development"
    DATA_DIR: str = ""

    DEMO_USER_EMAIL: str = "demo@datanova.ai"
    DEMO_USER_PASSWORD: str = "Demo@12345"
    DEMO_USER_NAME: str = "Demo User"

    model_config = SettingsConfigDict(
        env_file=(
            str(BACKEND_DIR / ".env"),
            str(ROOT_DIR / ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
