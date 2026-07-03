"""Pydantic schemas for the navigation API."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class GeoPointSchema(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in degrees")


class PlanMissionRequest(BaseModel):
    boundary: List[GeoPointSchema] = Field(
        ..., min_length=3, description="Polygon vertices defining the area to cover",
    )
    photos_per_m2: float = Field(
        default=0.5, gt=0, description="Desired photo density (photos/m²)",
    )
    altitude_m: float | None = Field(
        default=None, description="Fixed flight altitude (m). If null, calculated automatically",
    )
    overlap_front: float = Field(
        default=0.75, ge=0, le=0.99, description="Front overlap ratio for photos",
    )
    overlap_side: float = Field(
        default=0.60, ge=0, le=0.99, description="Side overlap ratio between passes",
    )
    speed_mps: float = Field(
        default=10.0, gt=0, description="Flight speed in m/s",
    )
    margin_m: float = Field(
        default=0.0, ge=0, description="Inset margin from boundary (m)",
    )

    model_config = {"populate_by_name": True}


class WaypointSchema(BaseModel):
    lat: float
    lon: float
    altitude_meters: float = Field(alias="altitudeMeters")
    heading_deg: float = Field(alias="headingDeg")
    trigger_camera: bool = Field(alias="triggerCamera")
    speed_mps: float | None = Field(default=None, alias="speedMps")

    model_config = {"populate_by_name": True}


class MissionStats(BaseModel):
    area_square_meters: float = Field(alias="areaSquareMeters")
    altitude_meters: float = Field(alias="altitudeMeters")
    total_distance_meters: float = Field(alias="totalDistanceMeters")
    estimated_time_seconds: float = Field(alias="estimatedTimeSeconds")
    photo_count: int = Field(alias="photoCount")
    photos_per_m2: float = Field(alias="photosPerM2")
    gsd_cm_per_pixel: float = Field(alias="gsdCmPerPixel")

    model_config = {"populate_by_name": True}


class CameraInfo(BaseModel):
    model: str
    sensor_width_mm: float = Field(alias="sensorWidthMm")
    sensor_height_mm: float = Field(alias="sensorHeightMm")
    focal_length_mm: float = Field(alias="focalLengthMm")
    image_width_px: int = Field(alias="imageWidthPx")
    image_height_px: int = Field(alias="imageHeightPx")

    model_config = {"populate_by_name": True}


class MissionParameters(BaseModel):
    overlap_front: float = Field(alias="overlapFront")
    overlap_side: float = Field(alias="overlapSide")
    flight_speed_mps: float = Field(alias="flightSpeedMps")
    margin_meters: float = Field(alias="marginMeters")

    model_config = {"populate_by_name": True}


class PlanMissionResponse(BaseModel):
    waypoints: List[WaypointSchema]
    stats: MissionStats
    camera: CameraInfo
    parameters: MissionParameters

    model_config = {"populate_by_name": True}
