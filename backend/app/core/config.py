from pydantic_settings import BaseSettings
from typing import Optional
import secrets
import sys


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://gymuser:gympass123@db:5432/gymtracker"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    # File Upload
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    UPLOAD_DIR: str = "/app/uploads"
    ALLOWED_IMAGE_EXTENSIONS: set = {".png", ".jpg", ".jpeg", ".gif"}

    # Email Configuration (Gmail SMTP)
    EMAIL_FROM: str = "your-email@gmail.com"  # Your Gmail address
    EMAIL_PASSWORD: str = "your-app-password"  # Gmail App Password (NOT your regular password)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    FRONTEND_URL: str = "http://localhost:8080"  # Frontend URL for reset links

    # Security
    MAX_LOGIN_ATTEMPTS: int = 5  # Maximum failed login attempts before lockout
    LOGIN_LOCKOUT_MINUTES: int = 15  # Lockout duration in minutes

    class Config:
        env_file = ".env"
        case_sensitive = True


def validate_security_settings(settings_obj: Settings) -> None:
    """Validate critical security settings on startup"""

    # Check if SECRET_KEY is the default value
    if settings_obj.SECRET_KEY == "your-secret-key-change-this-in-production":
        if settings_obj.ENVIRONMENT == "production":
            print("\n" + "="*70)
            print("CRITICAL SECURITY ERROR")
            print("="*70)
            print("SECRET_KEY is set to default value in PRODUCTION!")
            print("This is a critical security vulnerability.")
            print("\nTo fix:")
            print("1. Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(32))'")
            print("2. Set SECRET_KEY in your .env file")
            print("="*70 + "\n")
            sys.exit(1)
        else:
            print("\n" + "="*70)
            print("WARNING: Using default SECRET_KEY")
            print("="*70)
            print("This is OK for development, but MUST be changed for production!")
            print("\nTo generate a secure key:")
            print("python -c 'import secrets; print(secrets.token_urlsafe(32))'")
            print("="*70 + "\n")

    # Check if SECRET_KEY is long enough
    if len(settings_obj.SECRET_KEY) < 32:
        print("\n" + "="*70)
        print("WARNING: SECRET_KEY is too short")
        print("="*70)
        print(f"Current length: {len(settings_obj.SECRET_KEY)} characters")
        print("Recommended: 32+ characters")
        print("="*70 + "\n")


settings = Settings()
validate_security_settings(settings)
