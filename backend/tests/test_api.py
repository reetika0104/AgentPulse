"""
PULSE API Tests
Basic test suite for the PULSE backend API.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "PULSE" in data["name"]
    assert data["status"] == "running"


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


def test_login_valid_credentials():
    """Test login with valid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "pulse2026"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401


def test_protected_endpoint_without_token():
    """Test that protected endpoints require authentication."""
    response = client.get("/api/v1/brief/latest")
    assert response.status_code == 403


def test_protected_endpoint_with_token():
    """Test that protected endpoints work with valid token."""
    # Get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "pulse2026"},
    )
    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/api/v1/brief/latest",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_executions_endpoint():
    """Test executions list endpoint."""
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "pulse2026"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/executions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "executions" in data


def test_status_endpoint():
    """Test agent status endpoint."""
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "pulse2026"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent_name"] == "PULSE"
    assert data["status"] == "active"
