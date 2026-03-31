"""
Test main application setup.
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from config import settings


client = TestClient(app)


def test_health_check():
    """Test health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_cors_headers():
    """Test CORS headers are present."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_request_id_header():
    """Test request ID is added to responses."""
    response = client.get("/health")
    assert "x-request-id" in response.headers
    assert "x-api-version" in response.headers


def test_404_error():
    """Test 404 returns proper JSON error."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data or "detail" in data