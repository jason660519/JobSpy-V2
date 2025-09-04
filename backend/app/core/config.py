from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from pathlib import Path

class Settings(BaseSettings):
    # Application
    app_name: str = "JobSpy v2"
    app_version: str = "2.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Database
    database_url: str = "postgresql+asyncpg://jobspy:password@postgres:5432/jobspy"
    redis_url: str = "redis://redis:6379"
    database_echo: bool = False
    
    # AI Services
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-vision-preview"
    openai_max_tokens: int = 4000
    max_ai_cost_per_day: float = 50.0
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # API Settings
    api_v1_prefix: str = "/api/v1"
    max_requests_per_minute: int = 100
    max_ai_requests_per_day: int = 1000
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # Job Search Settings
    max_concurrent_searches: int = 5
    search_timeout_seconds: int = 30
    cache_ttl_seconds: int = 3600
    
    # File Storage
    upload_path: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for Alembic"""
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()