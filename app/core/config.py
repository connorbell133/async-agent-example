"""
Configuration Module

This module defines the application settings and configuration
using Pydantic BaseSettings for environment variable handling.
"""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # API configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Asynchronous Gemini Chatbot"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Google Gen AI SDK configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Task management
    TASK_CHECK_INTERVAL: int = int(os.getenv("TASK_CHECK_INTERVAL", "5"))  # seconds

    class Config:
        """Pydantic configuration class."""

        env_file = ".env"
        case_sensitive = True


# Create global settings object
settings = Settings()
