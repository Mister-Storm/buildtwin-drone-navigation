"""Tests for boustrophedon coverage path planning."""

from navigation.core.boustrophedon import generate_coverage_path
from shapely.geometry import Polygon


def test_generate_coverage_basic():
    """Simple square polygon generates waypoints."""
    poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
    path = generate_coverage_path(poly, spacing_m=20)
    assert len(path) > 0, "Should generate waypoints"
    # Each pass has 2 points (entry + exit), min 4 for 2 passes
    assert len(path) >= 4


def test_generate_coverage_spacing():
    """Tighter spacing produces more waypoints."""
    poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
    wide = generate_coverage_path(poly, spacing_m=50)
    tight = generate_coverage_path(poly, spacing_m=10)
    assert len(tight) > len(wide), "Tighter spacing should produce more waypoints"


def test_generate_coverage_empty_polygon():
    """Empty polygon returns empty path."""
    path = generate_coverage_path(Polygon(), spacing_m=20)
    assert path == []


def test_generate_coverage_margin():
    """Margin insets the polygon."""
    poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
    path_no_margin = generate_coverage_path(poly, spacing_m=30)
    path_margin = generate_coverage_path(poly, spacing_m=30, margin_m=10)
    # Both should produce valid paths
    assert len(path_no_margin) > 0
    assert len(path_margin) > 0


def test_generate_coverage_triangle():
    """Triangular polygon still generates coverage."""
    poly = Polygon([(0, 0), (50, 100), (100, 0)])
    path = generate_coverage_path(poly, spacing_m=20)
    assert len(path) > 0
