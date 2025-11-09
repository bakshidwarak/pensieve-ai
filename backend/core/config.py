"""Configuration management for Pensieve.ai backend."""

import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # App settings
    APP_NAME: str = "Pensieve.ai"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # AI Configuration
    OPENAI_API_KEY: str = ""
    TOGETHER_API_KEY: str = ""
    TAVILY_API_KEY: str = ""

    # Model settings
    OPENAI_MODEL: str = "gpt-4.1-mini"
    TOGETHER_MODEL: str = "openai/gpt-oss-20b"
    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"

    # RAG settings
    RAG_DATA_DIR: str = "data"
    CHUNK_SIZE: int = 300
    CHUNK_OVERLAP: int = 0

    # Database (if needed later)
    DATABASE_URL: str = "sqlite:///./pensieve.db"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
