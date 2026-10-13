from fastapi import APIRouter
from app.database import ping_database
from app.services.detection_service import detection_service
from app.services.ocr_service import ocr_service
from app.schemas import HealthResponse

router = APIRouter(tags=["System Health"])

@router.get("/health", response_model=HealthResponse)
@router.get("/api/v1/health", response_model=HealthResponse)
@router.get("/api/verification/health", response_model=HealthResponse)
async def check_health():
    """
    Returns live health status of database connectivity, YOLOv8 detection,
    Tesseract OCR, and Pillow EXIF processing.
    """
    db_ok, db_msg = ping_database()
    det_ok = detection_service.is_available
    ocr_ok = ocr_service.is_available
    exif_ok = True  # Pillow is always available in Python environment

    if db_ok and det_ok and ocr_ok:
        overall_status = "healthy"
    elif det_ok or ocr_ok:
        overall_status = "partially_available"
    else:
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        database_connected=db_ok,
        detection_available=det_ok,
        ocr_available=ocr_ok,
        exif_available=exif_ok,
        model="yolov8n",
        version="1.0.0",
        database_message=db_msg,
        detection_error=detection_service.error_message,
        ocr_error=ocr_service.error_message
    )
