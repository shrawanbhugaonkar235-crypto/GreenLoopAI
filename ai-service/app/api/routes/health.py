import os
from fastapi import APIRouter
from app.core.config import settings
from app.services.detection_service import detection_service

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint reporting readiness of internal AI services.
    Never exposes private API keys or sensitive file system paths.
    """
    openai_configured = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())
    yolo_available = detection_service.is_available()

    return {
        "status": "UP",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "components": {
            "openai_assistant": {
                "configured": openai_configured,
                "model": settings.OPENAI_MODEL
            },
            "yolo_detection": {
                "available": yolo_available
            },
            "ocr_engine": {
                "available": True
            },
            "authenticity_engine": {
                "available": True
            }
        }
    }
