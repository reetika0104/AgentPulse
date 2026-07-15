"""
PULSE Configuration Module
Centralized configuration management using Pydantic Settings.
Supports environment variables and AWS Secrets Manager.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "PULSE - AI Digital Chief of Staff"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = "pulse-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # Amazon Bedrock
    BEDROCK_MODEL_ID: str = "amazon.nova-micro-v1:0"
    BEDROCK_MAX_TOKENS: int = 4096

    # Amazon SES
    SES_SENDER_EMAIL: str = ""
    SES_RECIPIENT_EMAIL: str = ""

    # Amazon S3
    S3_BUCKET_NAME: str = "pulse-agent-briefs"

    # AWS Secrets Manager
    SECRETS_MANAGER_PREFIX: str = "pulse/"

    # Google Calendar
    GOOGLE_CALENDAR_CREDENTIALS: Optional[str] = None
    GOOGLE_CALENDAR_ID: str = "primary"

    # Gmail
    GMAIL_CREDENTIALS: Optional[str] = None

    # GitHub
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_USERNAME: Optional[str] = None

    # Weather
    WEATHER_API_KEY: Optional[str] = None
    WEATHER_CITY: str = "New York"

    # Notion
    NOTION_API_KEY: Optional[str] = None
    NOTION_DATABASE_ID: Optional[str] = None

    # RSS Feeds
    RSS_FEEDS: str = "https://feeds.feedburner.com/awsblog,https://blog.golang.org/feed.atom"

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # Slack
    SLACK_WEBHOOK_URL: Optional[str] = None

    # Scheduler
    SCHEDULE_CRON: str = "0 7 * * *"
    SCHEDULE_TIMEZONE: str = "America/New_York"

    # Database
    DATABASE_URL: str = "sqlite:///./pulse.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
