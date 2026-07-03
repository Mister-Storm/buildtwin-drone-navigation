"""Camera model and ground coverage calculations."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class CameraModel:
    """Physical camera model parameters."""
    sensor_width_mm: float
    sensor_height_mm: float
    focal_length_mm: float
    image_width_px: int
    image_height_px: int

    @property
    def aspect_ratio(self) -> float:
        return self.image_width_px / self.image_height_px

    def ground_sampling_distance(self, altitude_m: float) -> float:
        """GSD in meters per pixel at given altitude."""
        return (altitude_m * self.sensor_width_mm) / (self.focal_length_mm * self.image_width_px)

    def footprint_width_m(self, altitude_m: float) -> float:
        """Ground footprint width in meters at given altitude."""
        return self.ground_sampling_distance(altitude_m) * self.image_width_px

    def footprint_height_m(self, altitude_m: float) -> float:
        """Ground footprint height in meters at given altitude."""
        gsd = self.ground_sampling_distance(altitude_m)
        return gsd * self.image_height_px

    def footprint_area_m2(self, altitude_m: float) -> float:
        """Area covered by a single photo at given altitude."""
        return self.footprint_width_m(altitude_m) * self.footprint_height_m(altitude_m)

    def altitude_for_coverage(
        self,
        target_photos_per_m2: float,
        overlap_front: float = 0.75,
        overlap_side: float = 0.60,
    ) -> float:
        """Calculate altitude to achieve target photos per m².

        Args:
            target_photos_per_m2: Desired photo density (photos/m²).
            overlap_front: Overlap ratio between consecutive photos along flight path.
            overlap_side: Overlap ratio between adjacent passes.

        Returns:
            Altitude in meters.
        """
        # Effective area per photo accounting for overlap
        # A single photo covers footprint_area, but with overlaps each
        # photo contributes only (1-overlap_front)*(1-overlap_side) of its area
        effective_fraction = (1 - overlap_front) * (1 - overlap_side)

        # We need: photos = total_area / (effective_area_per_photo)
        # So: photos/m² = 1 / effective_area_per_photo
        # effective_area = footprint_area * effective_fraction
        # photos/m² = 1 / (footprint_area * effective_fraction)
        # footprint_area = 1 / (photos_m2 * effective_fraction)

        target_footprint_m2 = 1.0 / (target_photos_per_m2 * effective_fraction)

        # footprint = GSD*W * GSD*H = GSD² * W * H
        # GSD = sqrt(footprint / (W * H))
        # altitude = GSD * focal * W / sensor_W

        gsd = math.sqrt(target_footprint_m2 / (self.image_width_px * self.image_height_px))
        altitude = (gsd * self.focal_length_mm * self.image_width_px) / self.sensor_width_mm
        return max(altitude, 10.0)  # Minimum 10m altitude

    def photo_spacing_m(
        self,
        altitude_m: float,
        overlap_front: float = 0.75,
        overlap_side: float = 0.60,
    ) -> tuple[float, float]:
        """Calculate along-track and cross-track spacing between photos.

        Returns:
            (along_track_spacing_m, cross_track_spacing_m)
        """
        fw = self.footprint_width_m(altitude_m)
        fh = self.footprint_height_m(altitude_m)
        along = fw * (1 - overlap_front)
        cross = fh * (1 - overlap_side)
        return (along, cross)


# Default camera: DJI Phantom 4 Pro
DEFAULT_CAMERA = CameraModel(
    sensor_width_mm=13.2,
    sensor_height_mm=8.8,
    focal_length_mm=8.8,
    image_width_px=5472,
    image_height_px=3648,
)
