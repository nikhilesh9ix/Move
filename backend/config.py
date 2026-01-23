"""
Configuration management for the AI Stock Movement Explanation Engine.
Loads environment variables and provides centralized configuration.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    newsapi_key: str
    openrouter_api_key: str

    # AI Model Configuration
    ai_model: str = "meta-llama/llama-3-8b-instruct"
    ai_temperature: float = 0.2
    ai_max_tokens: int = 600

    # API Configuration
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
