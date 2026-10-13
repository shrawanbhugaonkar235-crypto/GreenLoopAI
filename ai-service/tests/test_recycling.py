import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.repositories.recycling_repository import RecyclingRepository
from app.services.recycling_service import recycling_service
from app.models.recycling import RecyclabilityStatusEnum, WarningSeverityEnum

from sqlalchemy.pool import StaticPool

AUTH_HEADERS = {"X-Service-Token": settings.FASTAPI_SERVICE_TOKEN or "dev-internal-secret-token"}

# Setup in-memory test database with thread-safe StaticPool
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def seed_test_db():
    db = TestingSessionLocal()
    repo = RecyclingRepository(db)
    repo.seed_default_knowledge_if_empty()
    db.close()


def test_list_recycling_categories():
    response = client.get("/api/v1/recycling/categories", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total"] >= 8
    slugs = [c["slug"] for c in data["categories"]]
    assert "plastic-bottles-containers" in slugs
    assert "paper-cardboard" in slugs
    assert "glass-bottles-jars" in slugs
    assert "metal-cans-packaging" in slugs
    assert "e-waste" in slugs
    assert "batteries" in slugs
    assert "organic-wet-waste" in slugs
    assert "hazardous-waste" in slugs


def test_get_category_guide_by_slug():
    response = client.get("/api/v1/recycling/categories/plastic-bottles-containers", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["category_slug"] == "plastic-bottles-containers"
    assert data["recyclability_status"] == "RECYCLABLE"
    assert len(data["steps"]) >= 4
    assert len(data["warnings"]) >= 1
    assert data["disposal_method"]["primary_route"] is not None


def test_get_category_guide_invalid_slug():
    response = client.get("/api/v1/recycling/categories/nonexistent-slug-xyz", headers=AUTH_HEADERS)
    assert response.status_code == 404


def test_get_guide_for_waste_type_plastic():
    response = client.get("/api/v1/recycling/guide/bottle?confidence=0.88", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["category_slug"] == "plastic-bottles-containers"
    assert data["recyclability_status"] == "RECYCLABLE"


def test_get_guide_for_waste_type_ewaste():
    response = client.get("/api/v1/recycling/guide/phone?confidence=0.92", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["category_slug"] == "e-waste"
    assert data["recyclability_status"] == "SPECIAL_HANDLING"
    assert any("Data Safety" in s["title"] for s in data["steps"])


def test_get_guide_for_waste_type_battery():
    response = client.get("/api/v1/recycling/guide/battery?confidence=0.85", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["category_slug"] == "batteries"
    assert data["recyclability_status"] == "SPECIAL_HANDLING"
    assert any(w["severity"] in ["DANGER", "WARNING"] for w in data["warnings"])


def test_get_guide_low_confidence_fallback():
    response = client.get("/api/v1/recycling/guide/unclear_item?confidence=0.10", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["recyclability_status"] == "UNKNOWN"
    assert "Low-Confidence" in data["title"]


def test_recommendation_endpoint():
    payload = {
        "waste_category": "Paper / Cardboard",
        "detected_label": "Box",
        "confidence": 0.89
    }
    response = client.post("/api/v1/recycling/recommendation", headers=AUTH_HEADERS, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["category_slug"] == "paper-cardboard"
    assert data["recyclability_status"] == "RECYCLABLE"
