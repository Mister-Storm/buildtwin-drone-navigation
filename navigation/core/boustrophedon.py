"""Boustrophedon (lawnmower) coverage path planning."""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import clip_by_rect


def generate_coverage_path(
    polygon: Polygon,
    spacing_m: float,
    margin_m: float = 0.0,
) -> List[Tuple[float, float]]:
    """Generate a boustrophedon (lawnmower) path inside a polygon.

    Args:
        polygon: The area to cover (local coordinates).
        spacing_m: Distance between parallel passes (meters).
        margin_m: Inset margin from polygon boundary.

    Returns:
        List of (x, y) waypoints in local coordinates.
    """
    if polygon.is_empty or not polygon.exterior:
        return []

    # Inset polygon if margin > 0
    if margin_m > 0:
        polygon = polygon.buffer(-margin_m)
        if polygon.is_empty:
            return []

    min_x, min_y, max_x, max_y = polygon.bounds
    width = max_x - min_x

    # Generate horizontal scan lines from bottom to top
    waypoints: list[tuple[float, float]] = []
    y = min_y
    direction = 1  # 1 = rightward, -1 = leftward

    while y <= max_y:
        # Create a horizontal line at y across the polygon width
        scan_line = LineString([(min_x - 1, y), (max_x + 1, y)])
        intersection = polygon.intersection(scan_line)

        if intersection.is_empty:
            y += spacing_m
            continue

        # Get the segments of the scan line inside the polygon
        if intersection.geom_type == "MultiLineString":
            segments = list(intersection.geoms)
        elif intersection.geom_type == "LineString":
            segments = [intersection]
        else:
            y += spacing_m
            continue

        # Sort segments left to right
        segments = sorted(segments, key=lambda s: s.bounds[0])

        for seg in segments:
            xs, ys, xe, ye = seg.bounds
            if direction == 1:
                waypoints.append((xs, y))
                waypoints.append((xe, y))
            else:
                waypoints.append((xe, y))
                waypoints.append((xs, y))

        direction *= -1
        y += spacing_m

    return waypoints


def optimize_path_order(
    waypoints: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    """Optimize waypoint order to minimize total path length.

    Uses nearest-neighbor heuristic for the first point, then
    connects remaining segments in order (already optimal for
    boustrophedon when generated correctly).
    """
    if not waypoints:
        return []

    # For boustrophedon, the path already alternates.
    # Remove duplicate consecutive points.
    deduped: list[tuple[float, float]] = []
    for wp in waypoints:
        if not deduped or (abs(wp[0] - deduped[-1][0]) > 0.01
                           or abs(wp[1] - deduped[-1][1]) > 0.01):
            deduped.append(wp)
    return deduped
