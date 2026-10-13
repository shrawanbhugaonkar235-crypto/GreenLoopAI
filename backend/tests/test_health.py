def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "partially_available")
    assert data["database_connected"] is True
    assert data["detection_available"] is True
    assert data["ocr_available"] is True
    assert data["exif_available"] is True
    assert data["model"] == "yolov8n"
