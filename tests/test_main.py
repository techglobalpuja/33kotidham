import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to 33 Koti Dham API"
    assert data["version"] == "1.0.0"


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_pujas():
    """Test get pujas endpoint."""
    response = client.get("/api/v1/pujas/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_plans():
    """Test get plans endpoint."""
    response = client.get("/api/v1/plans/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_chadawas():
    """Test get chadawas endpoint."""
    response = client.get("/api/v1/chadawas/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
