"""Geospatial geometry utilities for drone navigation."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from shapely import affinity
from shapely.geometry import Point, Polygon, box, mapping
from shapely.ops import clip_by_rect, orient, unary_union

# Earth radius in meters
EARTH_RADIUS_M = 6_371_000


@dataclass(frozen=True)
class GeoPoint:
    lat: float   # degrees
    lon: float   # degrees


@dataclass(frozen=True)
class Waypoint:
    lat: float       # degrees
    lon: float       # degrees
    altitude_m: float
    heading_deg: float = 0.0
    trigger_camera: bool = False
    speed_mps: float | None = None


def haversine_distance_m(p1: GeoPoint, p2: GeoPoint) -> float:
    """Haversine distance between two geo points in meters."""
    lat1, lon1 = math.radians(p1.lat), math.radians(p1.lon)
    lat2, lon2 = math.radians(p2.lat), math.radians(p2.lon)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def bearing_deg(p1: GeoPoint, p2: GeoPoint) -> float:
    """Bearing from p1 to p2 in degrees."""
    lat1, lon1 = math.radians(p1.lat), math.radians(p1.lon)
    lat2, lon2 = math.radians(p2.lat), math.radians(p2.lon)
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def destination_point(p: GeoPoint, bearing_deg: float, distance_m: float) -> GeoPoint:
    """Calculate destination point given start, bearing, and distance in meters."""
    lat1 = math.radians(p.lat)
    lon1 = math.radians(p.lon)
    bearing = math.radians(bearing_deg)
    angular_distance = distance_m / EARTH_RADIUS_M

    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular_distance)
        + math.cos(lat1) * math.sin(angular_distance) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(angular_distance) * math.cos(lat1),
        math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2),
    )
    return GeoPoint(lat=math.degrees(lat2), lon=math.degrees(lon2))


def polygon_centroid(points: list[GeoPoint]) -> GeoPoint:
    """Centroid of a polygon defined by a list of points."""
    shapely_poly = Polygon([(p.lon, p.lat) for p in points])
    c = shapely_poly.centroid
    return GeoPoint(lat=c.y, lon=c.x)


def polygon_area_m2(points: list[GeoPoint]) -> float:
    """Approximate area of a geo-referenced polygon in square meters."""
    if len(points) < 3:
        return 0.0
    cent = polygon_centroid(points)

    # Project to local Cartesian plane around centroid
    projected = []
    for p in points:
        dx = haversine_distance_m(cent, GeoPoint(cent.lat, p.lon))
        if p.lon < cent.lon:
            dx = -dx
        dy = haversine_distance_m(cent, GeoPoint(p.lat, cent.lon))
        if p.lat < cent.lat:
            dy = -dy
        projected.append((dx, dy))

    # Shoelace formula
    n = len(projected)
    area = 0.0
    for i in range(n):
        x1, y1 = projected[i]
        x2, y2 = projected[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def project_polygon(points: list[GeoPoint]) -> tuple[Polygon, GeoPoint, float]:
    """Project a geo polygon to local Cartesian coordinates.

    Returns (local_polygon, origin, rotation_deg).
    """
    cent = polygon_centroid(points)
    # Find dominant edge direction for rotation alignment
    best_angle = 0.0
    best_width = float("inf")

    for deg in range(0, 180, 5):
        local = _project_to_local(points, cent)
        poly = Polygon(local)
        rotated = affinity.rotate(poly, deg, origin="centroid", use_radians=False)
        min_x, min_y, max_x, max_y = rotated.bounds
        width = max_x - min_x
        if width < best_width:
            best_width = width
            best_angle = deg

    local = _project_to_local(points, cent)
    poly = Polygon(local)
    rotated = affinity.rotate(poly, best_angle, origin="centroid", use_radians=False)
    return rotated, cent, best_angle


def _project_to_local(points: list[GeoPoint], origin: GeoPoint) -> list[tuple[float, float]]:
    result = []
    for p in points:
        dx = haversine_distance_m(origin, GeoPoint(origin.lat, p.lon))
        if p.lon < origin.lon:
            dx = -dx
        dy = haversine_distance_m(origin, GeoPoint(p.lat, origin.lon))
        if p.lat < origin.lat:
            dy = -dy
        result.append((dx, dy))
    return result


def unproject_waypoint(
    local_x: float,
    local_y: float,
    origin: GeoPoint,
    rotation_deg: float,
) -> GeoPoint:
    """Convert a local (x, y) coordinate back to lat/lon."""
    # Reverse rotation
    rad = math.radians(rotation_deg)
    rx = local_x * math.cos(rad) + local_y * math.sin(rad)
    ry = -local_x * math.sin(rad) + local_y * math.cos(rad)

    # Reverse projection
    p = GeoPoint(
        lat=origin.lat + (ry / EARTH_RADIUS_M) * (180.0 / math.pi),
        lon=origin.lon + (rx / EARTH_RADIUS_M) * (180.0 / math.pi) / math.cos(math.radians(origin.lat)),
    )
    return p
