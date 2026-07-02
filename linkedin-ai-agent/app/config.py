"""
Application configuration using Pydantic Settings.
Loads from environment variables and .env file.
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_key: str

    # Notion
    notion_api_key: str = ""
    notion_database_id: str = ""

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # App
    app_name: str = "LinkedIn Growth AI Agent"
    app_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"

    # API
    api_v1_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000

    # Rate Limiting
    rate_limit_requests_per_minute: int = 60

    # CORS
    cors_origins: str = "*"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
