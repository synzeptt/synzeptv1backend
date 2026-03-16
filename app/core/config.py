import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Synzept"
    PROJECT_VERSION: str = "0.1.0"

    # For local development, default to SQLite. Set DATABASE_URL in environment for Postgres in production.
    DATABASE_URL: str = Field("sqlite:///./synzept.db", env="DATABASE_URL")

    # Secrets
    JWT_SECRET: str = Field("changeme", env="JWT_SECRET")
    JWT_ALGORITHM: str = "HS256"

    # Google OAuth settings
    GOOGLE_CLIENT_ID: str | None = Field(None, env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str | None = Field(None, env="GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = Field("http://localhost:3000/auth/google/callback", env="GOOGLE_REDIRECT_URI")

    # CORS - comma separated list of allowed origins
    CORS_ORIGINS: str = Field("https://synzept.com,https://www.synzept.com,http://localhost:3000,http://localhost:3001", env="CORS_ORIGINS")

    class Config:
        env_file = ".env"


settings = Settings()
