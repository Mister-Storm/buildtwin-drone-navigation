"""Tests for navigation geometry module."""

from navigation.core.geometry import GeoPoint, haversine_distance_m, polygon_area_m2


def test_haversine_same_point():
    """Distance from a point to itself should be 0."""
    p = GeoPoint(lat=-23.5505, lon=-46.6333)
    assert haversine_distance_m(p, p) == 0.0


def test_haversine_known_distance():
    """Distance between two known points in São Paulo."""
    p1 = GeoPoint(lat=-23.5505, lon=-46.6333)  # Centro SP
    p2 = GeoPoint(lat=-23.5610, lon=-46.6560)  # aprox 2.5km SW
    dist = haversine_distance_m(p1, p2)
    assert 2000 < dist < 3000, f"Expected ~2.5km, got {dist}m"


def test_polygon_area():
    """Square with 0.00045 deg sides near SP should be ~9,180 m²."""
    lat, lon = -23.5505, -46.6333
    delta = 0.00045  # ~45-50m
    points = [
        GeoPoint(lat - delta, lon - delta),
        GeoPoint(lat - delta, lon + delta),
        GeoPoint(lat + delta, lon + delta),
        GeoPoint(lat + delta, lon - delta),
    ]
    area = polygon_area_m2(points)
    assert 8000 < area < 10500, f"Expected ~9,200 m², got {area:.0f} m²"


def test_camera_gsd():
    """DJI Phantom 4 Pro at 80m should have GSD ~2cm."""
    from navigation.core.camera import DEFAULT_CAMERA
    gsd = DEFAULT_CAMERA.ground_sampling_distance(80.0)
    assert 0.015 < gsd < 0.025, f"Expected ~2cm/px, got {gsd*100:.2f}cm/px"


def test_camera_footprint():
    """Footprint area at 80m should be reasonable."""
    from navigation.core.camera import DEFAULT_CAMERA
    area = DEFAULT_CAMERA.footprint_area_m2(80.0)
    assert 5000 < area < 15000, f"Expected ~9,600 m², got {area:.0f} m²"
