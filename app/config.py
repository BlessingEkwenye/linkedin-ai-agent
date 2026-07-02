"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4o"
    
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    
    notion_api_key: str = ""
    notion_database_id: str = ""
    
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    app_name: str = "LinkedIn Growth AI Agent"
    app_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"
    
    api_v1_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    
    cors_origins: str = "*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
