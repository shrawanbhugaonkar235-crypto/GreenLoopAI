import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base backend directory
BACKEND_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # MongoDB Atlas Database
    MONGODB_URI: str = "mock"
    MONGODB_DATABASE: str = "greenloopai"

    # JWT Authentication
    JWT_SECRET_KEY: str = "greenloopai-super-secret-jwt-key-2026-production-token"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # AI Pipeline
    YOLO_MODEL_PATH: str = str(BACKEND_DIR / "models" / "yolov8n.pt")
    YOLO_CONF: float = 0.25
    TESSERACT_CMD: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # CORS
    FRONTEND_ORIGINS: str = (
        "http://localhost:3000,http://localhost:5000,http://localhost:8000,"
        "http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5000,http://127.0.0.1:8000"
    )

    # Limits & Rewards
    MAX_UPLOAD_MB: int = 10
    GREENCOINS_PER_SCORE: float = 0.5

    @property
    def allowed_origins(self) -> List[str]:
        if not self.FRONTEND_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",") if origin.strip()]

    @property
    def resolved_yolo_path(self) -> str:
        # Check explicit path
        if os.path.exists(self.YOLO_MODEL_PATH):
            return self.YOLO_MODEL_PATH
        
        # Check relative to backend dir
        candidate = BACKEND_DIR / self.YOLO_MODEL_PATH
        if candidate.exists():
            return str(candidate)

        # Check candidate in ai-service if legacy exists
        candidate_legacy = BACKEND_DIR.parent / "ai-service" / "models" / "yolov8n.pt"
        if candidate_legacy.exists():
            return str(candidate_legacy)

        return self.YOLO_MODEL_PATH

settings = Settings()
