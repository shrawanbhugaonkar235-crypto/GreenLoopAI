import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


AUTH_HEADERS = {"X-Service-Token": settings.FASTAPI_SERVICE_TOKEN or "dev-internal-secret-token"}


def test_verify_empty_file():
    response = client.post(
        "/api/v1/verification/verify",
        headers=AUTH_HEADERS,
        files={"image": ("empty.jpg", b"", "image/jpeg")}
    )
    assert response.status_code == 400
    assert "empty" in response.text.lower()


def test_verify_invalid_file_type():
    response = client.post(
        "/api/v1/verification/verify",
        headers=AUTH_HEADERS,
        files={"image": ("document.txt", b"This is plain text, not an image.", "text/plain")}
    )
    assert response.status_code == 400
    assert "unsupported" in response.text.lower() or "invalid" in response.text.lower()


def test_verify_model_unavailable(monkeypatch):
    from app.services.detection_service import detection_service
    monkeypatch.setattr(detection_service, "is_available", lambda: False)

    img = Image.new("RGB", (100, 100), color=(73, 109, 137))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    response = client.post(
        "/api/v1/verification/verify",
        headers=AUTH_HEADERS,
        files={"image": ("test.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 503
    assert "AI detection model unavailable" in response.text


def test_verify_real_image_success():
    img = Image.new("RGB", (320, 240), color=(100, 150, 200))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    response = client.post(
        "/api/v1/verification/verify",
        headers=AUTH_HEADERS,
        files={"image": ("sample_waste.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "verification_id" in data
    assert "verification_score" in data
    assert "status" in data
    assert "authenticity" in data
    assert "brand_detection" in data
    assert "reward" in data
    assert "score_breakdown" in data


def test_ocr_and_barcode_scanner():
    from app.services.ocr_service import ocr_service
    # Blank test image
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    res = ocr_service.extract_text_and_brand(img)
    assert res.status in ["NOT_DETECTED", "DETECTED"]

