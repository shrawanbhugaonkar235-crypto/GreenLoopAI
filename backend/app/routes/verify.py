import os
import uuid
import tempfile
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from PIL import Image

from app.config import settings
from app.database import get_db, get_user_balance
from app.auth import get_current_user
from app.schemas import VerificationResponse
from app.services.detection_service import detection_service
from app.services.ocr_service import ocr_service
from app.services.authenticity_service import authenticity_service
from app.services.scoring_service import scoring_service

logger = logging.getLogger("greenloopai.verify")

router = APIRouter(tags=["Waste Verification"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}

@router.post("/api/v1/verify", response_model=VerificationResponse)
@router.post("/api/verification/verify", response_model=VerificationResponse)
async def verify_waste(
    image: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None),
    citizen_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Authenticates the citizen, validates image content and file size (max 10MB),
    executes the real AI pipeline (YOLOv8 + Tesseract OCR + Pillow EXIF),
    calculates composite score V, stores records in MongoDB, and issues GreenCoins.
    """
    upload = image or file
    if not upload or not upload.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An image file is required for waste verification."
        )

    # 1. Validate file extension & mime type
    filename = upload.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: JPG, JPEG, PNG, WEBP."
        )

    # 2. Check availability of underlying models/engines
    if not detection_service.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Object detection model is unavailable: {detection_service.error_message}"
        )
    if not ocr_service.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OCR engine is unavailable: {ocr_service.error_message}"
        )

    # 3. Read content and enforce size limit
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    content = await upload.read()
    file_size = len(content)
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image size ({file_size / (1024*1024):.1f} MB) exceeds maximum allowed limit of {settings.MAX_UPLOAD_MB} MB."
        )
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty."
        )

    # 4. Save to temporary storage and inspect with Pillow
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    temp_path = temp_file.name
    try:
        temp_file.write(content)
        temp_file.flush()
        temp_file.close()

        try:
            pil_image = Image.open(temp_path)
            pil_image.verify()
            # Reopen for reading after verify
            pil_image = Image.open(temp_path)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Corrupt or invalid image file: {str(e)}"
            )

        # 5. Run YOLOv8 Object Detection
        try:
            detected_objects, primary_category, avg_confidence = detection_service.detect_objects(pil_image)
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Object detection failed: {str(e)}"
            )

        # 6. Run Tesseract OCR Text & Brand Extraction
        try:
            ocr_result = ocr_service.extract_text_and_brand(pil_image)
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OCR text extraction failed: {str(e)}"
            )

        # 7. Run Pillow EXIF Authenticity Check
        try:
            authenticity_signal = authenticity_service.verify_authenticity(pil_image)
        except Exception as e:
            logger.error(f"EXIF check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authenticity analysis failed: {str(e)}"
            )

        # 8. Compute Verification Score V & GreenCoins
        breakdown, coins, reward_tier, calculation_basis, is_verified, explanation = (
            scoring_service.calculate_score_and_reward(
                detected_objects=detected_objects,
                ocr_result=ocr_result,
                authenticity=authenticity_signal
            )
        )

        verification_id = str(uuid.uuid4())
        user_id = current_user["id"]
        now_iso = datetime.now(timezone.utc).isoformat()

        # Categories list
        categories_detected = list({obj.category for obj in detected_objects}) if detected_objects else []

        authenticity_label = (
            "High" if authenticity_signal.score >= 0.75
            else "Moderate" if authenticity_signal.score >= 0.50
            else "Low"
        )

        # 9. Save Verification record to MongoDB
        db = get_db()
        verification_doc = {
            "id": verification_id,
            "user_id": user_id,
            "citizen_id": user_id,
            "file_name": filename,
            "file_size": file_size,
            "timestamp": now_iso,
            "category": primary_category,
            "categories": categories_detected,
            "confidence": avg_confidence,
            "ocr_text": ocr_result.text if ocr_result.text else None,
            "brand": ocr_result.brand,
            "authenticity": authenticity_label,
            "score": breakdown.composite_score,
            "coins": coins,
            "reward_tier": reward_tier,
            "status": "verified" if is_verified else "rejected",
            "message": explanation,
            "detected_objects": [obj.model_dump() for obj in detected_objects],
            "ocr": ocr_result.model_dump(),
            "authenticity_detail": authenticity_signal.model_dump(),
            "breakdown": breakdown.model_dump(),
            "calculation_basis": calculation_basis,
            "created_at": now_iso
        }

        db.verifications.insert_one(verification_doc)

        # 10. Award GreenCoins if verified
        if is_verified and coins > 0:
            tx_doc = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "verification_id": verification_id,
                "file_name": filename,
                "description": f"Verified submission — {filename}",
                "category": primary_category or "Recyclable Waste",
                "reward_tier": reward_tier,
                "amount": coins,
                "type": "reward",
                "created_at": now_iso
            }
            try:
                db.greencoins_transactions.insert_one(tx_doc)
            except Exception as e:
                logger.warning(f"Transaction duplicate or insert note: {e}")

        # Compute updated balance
        balance = get_user_balance(user_id)

        # 11. Return response
        return VerificationResponse(
            id=verification_id,
            citizen_id=user_id,
            file_name=filename,
            file_size=file_size,
            timestamp=now_iso,
            category=primary_category,
            confidence=avg_confidence,
            ocr_text=ocr_result.text if ocr_result.text else None,
            brand=ocr_result.brand,
            authenticity=authenticity_label,
            score=breakdown.composite_score,
            coins=coins,
            reward_tier=reward_tier,
            status="verified" if is_verified else "rejected",
            message=explanation,
            detected_objects=detected_objects,
            ocr=ocr_result.model_dump(),
            authenticity_detail=authenticity_signal.model_dump(),
            breakdown=breakdown,
            calculation_basis=calculation_basis,
            balance=balance
        )

    finally:
        # Clean up temporary uploaded file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_path}: {e}")
