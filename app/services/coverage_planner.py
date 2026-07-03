"""Mission planning service — orchestrates path generation + camera calculation."""

from __future__ import annotations


from navigation.core.boustrophedon import generate_coverage_path, optimize_path_order
from navigation.core.camera import DEFAULT_CAMERA, CameraModel
from navigation.core.geometry import (
    GeoPoint,
    Waypoint,
    haversine_distance_m,
    polygon_area_m2,
    project_polygon,
    unproject_waypoint,
)


class MissionPlanner:
    """Plans drone missions: area polygon → waypoints with camera triggers."""

    def __init__(self, camera: CameraModel = DEFAULT_CAMERA):
        self._camera = camera

    def plan_mission(
        self,
        boundary_points: list[GeoPoint],
        photos_per_m2: float,
        altitude_m: float | None = None,
        overlap_front: float = 0.75,
        overlap_side: float = 0.60,
        speed_mps: float = 10.0,
        margin_m: float = 0.0,
    ) -> dict:
        """Plan a full mission from a boundary polygon.

        Args:
            boundary_points: Polygon vertices in lat/lon order (closed or open).
            photos_per_m2: Desired photo density.
            altitude_m: Fixed altitude. If None, calculated from photos_per_m2.
            overlap_front: Overlap along flight direction.
            overlap_side: Overlap between passes.
            speed_mps: Flight speed in m/s.
            margin_m: Inset margin from boundary.

        Returns:
            Mission dict with waypoints, stats, and metadata.
        """
        if len(boundary_points) < 3:
            return {"error": "Polygon must have at least 3 points"}

        # Close polygon if needed
        if (boundary_points[0].lat != boundary_points[-1].lat
                or boundary_points[0].lon != boundary_points[-1].lon):
            boundary_points = list(boundary_points) + [boundary_points[0]]

        # Calculate area
        area_m2 = polygon_area_m2(boundary_points)

        # Determine altitude
        if altitude_m is None or altitude_m <= 0:
            altitude_m = self._camera.altitude_for_coverage(
                photos_per_m2, overlap_front, overlap_side,
            )

        # Calculate spacings
        along_spacing, cross_spacing = self._camera.photo_spacing_m(
            altitude_m, overlap_front, overlap_side,
        )

        # Project polygon to local coordinates
        local_poly, origin, rotation = project_polygon(boundary_points)

        # Generate coverage path
        path_local = generate_coverage_path(local_poly, cross_spacing, margin_m)
        path_local = optimize_path_order(path_local)

        if not path_local:
            return {"error": "No coverage path generated"}

        # Convert local path to geo waypoints + camera triggers
        waypoints: list[Waypoint] = []
        previous: tuple[float, float] | None = None
        total_distance_m = 0.0

        for i, (x, y) in enumerate(path_local):
            gp = unproject_waypoint(x, y, origin, rotation)
            heading = 0.0

            if previous is not None:
                # Calculate heading from previous point
                prev_gp = unproject_waypoint(*previous, origin, rotation)
                heading = self._bearing(prev_gp, gp)
                seg_distance = haversine_distance_m(prev_gp, gp)
                total_distance_m += seg_distance

                # Calculate camera triggers along this segment
                if seg_distance > 0:
                    # Number of photos along this segment
                    n_photos = max(1, int(seg_distance / along_spacing))
                    for p_idx in range(n_photos):
                        fraction = (p_idx + 1) / n_photos
                        lat = prev_gp.lat + (gp.lat - prev_gp.lat) * fraction
                        lon = prev_gp.lon + (gp.lon - prev_gp.lon) * fraction
                        waypoints.append(Waypoint(
                            lat=lat,
                            lon=lon,
                            altitude_m=altitude_m,
                            heading_deg=heading,
                            trigger_camera=True,
                            speed_mps=speed_mps,
                        ))

            # Add the waypoint itself (turning point - no camera)
            waypoints.append(Waypoint(
                lat=gp.lat,
                lon=gp.lon,
                altitude_m=altitude_m,
                heading_deg=heading,
                trigger_camera=False,
                speed_mps=speed_mps,
            ))
            previous = (x, y)

        # Calculate stats
        gsd = self._camera.ground_sampling_distance(altitude_m)
        photo_count = sum(1 for wp in waypoints if wp.trigger_camera)
        estimated_time_s = total_distance_m / speed_mps if speed_mps > 0 else 0

        return {
            "waypoints": [
                {
                    "lat": wp.lat,
                    "lon": wp.lon,
                    "altitudeMeters": wp.altitude_m,
                    "headingDeg": round(wp.heading_deg, 1),
                    "triggerCamera": wp.trigger_camera,
                    "speedMps": wp.speed_mps,
                }
                for wp in waypoints
            ],
            "stats": {
                "areaSquareMeters": round(area_m2, 2),
                "altitudeMeters": round(altitude_m, 1),
                "totalDistanceMeters": round(total_distance_m, 1),
                "estimatedTimeSeconds": round(estimated_time_s, 0),
                "photoCount": photo_count,
                "photosPerM2": round(photo_count / area_m2, 4) if area_m2 > 0 else 0,
                "gsdCmPerPixel": round(gsd * 100, 2),
            },
            "camera": {
                "model": "DJI Phantom 4 Pro",
                "sensorWidthMm": self._camera.sensor_width_mm,
                "sensorHeightMm": self._camera.sensor_height_mm,
                "focalLengthMm": self._camera.focal_length_mm,
                "imageWidthPx": self._camera.image_width_px,
                "imageHeightPx": self._camera.image_height_px,
            },
            "parameters": {
                "overlapFront": overlap_front,
                "overlapSide": overlap_side,
                "flightSpeedMps": speed_mps,
                "marginMeters": margin_m,
            },
        }

    def _bearing(self, p1: GeoPoint, p2: GeoPoint) -> float:
        from navigation.core.geometry import bearing_deg
        return bearing_deg(p1, p2)
