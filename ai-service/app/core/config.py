import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "GreenLoopAI AI Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Computer Vision / YOLO Configuration
    YOLO_MODEL_PATH: Optional[str] = "models/yolov8n.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.20
    
    # Internal Service Authentication (Security Gateway -> FastAPI)
    FASTAPI_SERVICE_TOKEN: Optional[str] = None
    
    # Image Upload and Processing Constraints
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp"]
    ALLOWED_MIME_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    @field_validator("MAX_UPLOAD_SIZE", mode="before")
    @classmethod
    def _parse_size(cls, v):
        if isinstance(v, str):
            v_clean = v.strip().upper()
            if v_clean.endswith("MB"):
                return int(float(v_clean[:-2])) * 1024 * 1024
            elif v_clean.endswith("KB"):
                return int(float(v_clean[:-2])) * 1024
            elif v_clean.endswith("GB"):
                return int(float(v_clean[:-2])) * 1024 * 1024 * 1024
            return int(v_clean)
        return int(v)
    
    # Chat & Assistant Limits
    MAX_MESSAGE_LENGTH: int = 2000
    MAX_CHAT_HISTORY: int = 10
    ASSISTANT_TIMEOUT_SECONDS: float = 30.0
    
    # Rate Limiting (In-memory token bucket)
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    # Database Configuration (PostgreSQL / Relational Store)
    DATABASE_URL: str = "sqlite:///./greenloop.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # Security & Identity Validation
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
