from pydantic_settings import BaseSettings
from typing import Optional


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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
