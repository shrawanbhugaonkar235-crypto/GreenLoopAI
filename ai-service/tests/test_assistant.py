import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.utils.security import sanitize_text_input

client = TestClient(app)


AUTH_HEADERS = {"X-Service-Token": settings.FASTAPI_SERVICE_TOKEN or "dev-internal-secret-token"}


def test_sanitize_text_input():
    dirty = "Hello\x00\x08World!\nHow are you?"
    clean = sanitize_text_input(dirty)
    assert clean == "HelloWorld!\nHow are you?"


def test_assistant_empty_message():
    response = client.post("/api/v1/assistant/chat", headers=AUTH_HEADERS, json={})
    assert response.status_code in [400, 422]


def test_assistant_missing_api_key(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", None)
    response = client.post("/api/v1/assistant/chat", headers=AUTH_HEADERS, json={"message": "What is GreenLoopAI?"})
    # When API key is not configured, it returns 503 AI_SERVICE_NOT_CONFIGURED
    assert response.status_code == 503
    assert "AI_SERVICE_NOT_CONFIGURED" in response.text
