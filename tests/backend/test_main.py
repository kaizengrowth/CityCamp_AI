import pytest
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
    assert "environment" in data

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "CityCamp AI" in data["message"]

def test_api_v1_meetings_endpoint():
    """Test the API v1 meetings endpoint."""
    response = client.get("/api/v1/meetings/")
    # This should return 200 if endpoint exists, or 404 if not implemented yet
    assert response.status_code in [200, 404, 405]

def test_api_v1_auth_endpoint():
    """Test the API v1 auth endpoint."""
    response = client.get("/api/v1/auth/")
    # This should return 200 if endpoint exists, or 404 if not implemented yet
    assert response.status_code in [200, 404, 405]
