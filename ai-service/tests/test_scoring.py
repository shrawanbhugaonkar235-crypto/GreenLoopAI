import pytest
from app.services.scoring_service import scoring_service
from app.schemas.verification import DetectedObject, OcrResult, AuthenticitySignal


def test_scoring_with_full_signals():
    detected_objects = [
        DetectedObject(label="Bottle", confidence=0.92, category="Plastic")
    ]
    ocr_result = OcrResult(
        text="Coca-Cola 500ml",
        brand="Coca-Cola",
        confidence=0.90,
        status="DETECTED"
    )
    authenticity = AuthenticitySignal(
        exif_present=True,
        camera_make="Apple",
        camera_model="iPhone 14",
        timestamp_valid=True,
        score=0.90,
        flags=[]
    )

    breakdown, reward, verified = scoring_service.calculate_score_and_reward(
        detected_objects=detected_objects,
        ocr_result=ocr_result,
        authenticity=authenticity
    )

    # 92 * 0.45 = 41.4
    # 90 * 0.30 = 27.0
    # 90 * 0.25 = 22.5
    # Total ~ 90.9
    assert verified is True
    assert breakdown.composite_score >= 85.0
    assert reward.reward_tier == "PLATINUM"
    assert reward.greencoins_awarded > 30


def test_scoring_with_no_detection():
    detected_objects = []
    ocr_result = OcrResult(status="NOT_DETECTED")
    authenticity = AuthenticitySignal(
        exif_present=False,
        timestamp_valid=False,
        score=0.50,
        flags=["No hardware EXIF metadata found"]
    )

    breakdown, reward, verified = scoring_service.calculate_score_and_reward(
        detected_objects=detected_objects,
        ocr_result=ocr_result,
        authenticity=authenticity
    )

    assert verified is False
    assert breakdown.composite_score < 60.0
