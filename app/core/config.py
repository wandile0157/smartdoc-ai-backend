"""
Configuration management for SmartDoc AI
Handles environment variables and application settings
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Application Info
    APP_NAME: str = "SmartDoc AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # CORS Settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    # File Upload Settings
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: list = [".txt", ".pdf", ".docx", ".doc"]
    
    # Database Settings
    DATABASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings instance.
    
    Returns:
        Settings: Application settings
    """
    return settings

