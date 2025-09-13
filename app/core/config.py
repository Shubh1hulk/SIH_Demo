"""
Core configuration module for the Healthcare Chatbot
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app config
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-here"
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./healthcare_chatbot.db"
    
    # External APIs
    GOVERNMENT_HEALTH_API_URL: str = "https://api.gov.health.example.com"
    GOVERNMENT_HEALTH_API_KEY: str = ""
    
    # WhatsApp Business API
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = ""
    
    # Twilio SMS
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # Redis for caching
    REDIS_URL: str = "redis://localhost:6379"
    
    # Supported languages
    SUPPORTED_LANGUAGES: str = "en,hi,ta,te,bn,gu,mr,ml,kn,pa"
    
    # Cloud configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = ""
    
    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GOOGLE_CLOUD_PROJECT: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def supported_languages_list(self) -> List[str]:
        """Get list of supported languages"""
        return [lang.strip() for lang in self.SUPPORTED_LANGUAGES.split(",")]


settings = Settings()