from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_returns_status():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "components" in data
    assert "openai_assistant" in data["components"]
    assert "yolo_detection" in data["components"]


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ONLINE"
