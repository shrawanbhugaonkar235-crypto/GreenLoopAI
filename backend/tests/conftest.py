import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure mock db is used for test runs
os.environ["MONGODB_URI"] = "mock"

from app.main import app
from app.database import init_indexes

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    init_indexes()

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
