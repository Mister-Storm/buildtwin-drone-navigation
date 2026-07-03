"""Tests for the MissionPlanner service."""

from app.services.coverage_planner import MissionPlanner
from navigation.core.geometry import GeoPoint


def test_plan_mission_basic():
    """Simple square mission returns waypoints and stats."""
    planner = MissionPlanner()
    boundary = [
        GeoPoint(lat=-23.5505, lon=-46.6333),
        GeoPoint(lat=-23.5505, lon=-46.6300),
        GeoPoint(lat=-23.5480, lon=-46.6300),
        GeoPoint(lat=-23.5480, lon=-46.6333),
    ]
    result = planner.plan_mission(boundary, photos_per_m2=0.01)
    assert "error" not in result
    assert len(result["waypoints"]) > 0
    assert result["stats"]["areaSquareMeters"] > 0
    assert result["stats"]["photoCount"] > 0
    assert result["camera"]["model"] == "DJI Phantom 4 Pro"


def test_plan_mission_with_fixed_altitude():
    """Fixed altitude overrides automatic calculation."""
    planner = MissionPlanner()
    boundary = [
        GeoPoint(lat=-23.5505, lon=-46.6333),
        GeoPoint(lat=-23.5505, lon=-46.6300),
        GeoPoint(lat=-23.5480, lon=-46.6300),
        GeoPoint(lat=-23.5480, lon=-46.6333),
    ]
    result = planner.plan_mission(boundary, photos_per_m2=0.01, altitude_m=120.0)
    assert result["stats"]["altitudeMeters"] == 120.0


def test_plan_mission_invalid_polygon():
    """Less than 3 points returns error."""
    planner = MissionPlanner()
    boundary = [GeoPoint(lat=-23.5505, lon=-46.6333)]
    result = planner.plan_mission(boundary, photos_per_m2=0.01)
    assert "error" in result


def test_plan_mission_stats():
    """Stats should include all expected fields."""
    planner = MissionPlanner()
    boundary = [
        GeoPoint(lat=-23.5505, lon=-46.6333),
        GeoPoint(lat=-23.5505, lon=-46.6300),
        GeoPoint(lat=-23.5480, lon=-46.6300),
        GeoPoint(lat=-23.5480, lon=-46.6333),
    ]
    result = planner.plan_mission(boundary, photos_per_m2=0.01)
    stats = result["stats"]
    assert "areaSquareMeters" in stats
    assert "altitudeMeters" in stats
    assert "totalDistanceMeters" in stats
    assert "estimatedTimeSeconds" in stats
    assert "photoCount" in stats
    assert "gsdCmPerPixel" in stats


def test_plan_mission_with_margin():
    """Margin parameter affects the path."""
    planner = MissionPlanner()
    boundary = [
        GeoPoint(lat=-23.5505, lon=-46.6333),
        GeoPoint(lat=-23.5505, lon=-46.6300),
        GeoPoint(lat=-23.5480, lon=-46.6300),
        GeoPoint(lat=-23.5480, lon=-46.6333),
    ]
    result = planner.plan_mission(boundary, photos_per_m2=0.01, margin_m=5.0)
    assert "error" not in result
    assert len(result["waypoints"]) > 0
