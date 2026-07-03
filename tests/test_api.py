"""Tests for the FastAPI routes using TestClient."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    """GET /health returns ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_plan_mission_endpoint():
    """POST /plan-mission with valid polygon returns mission."""
    payload = {
        "boundary": [
            {"lat": -23.5505, "lon": -46.6333},
            {"lat": -23.5505, "lon": -46.6300},
            {"lat": -23.5480, "lon": -46.6300},
            {"lat": -23.5480, "lon": -46.6333},
        ],
        "photos_per_m2": 0.01,
    }
    response = client.post("/plan-mission", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "waypoints" in data
    assert "stats" in data
    assert "camera" in data
    assert "parameters" in data
    assert data["stats"]["areaSquareMeters"] > 0


def test_plan_mission_invalid():
    """POST /plan-mission with 2 points returns 400."""
    payload = {
        "boundary": [
            {"lat": -23.5505, "lon": -46.6333},
            {"lat": -23.5505, "lon": -46.6300},
        ],
    }
    response = client.post("/plan-mission", json=payload)
    assert response.status_code == 422  # Validation error
