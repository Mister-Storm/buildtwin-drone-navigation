"""API routes for drone navigation."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import PlanMissionRequest, PlanMissionResponse
from app.services.coverage_planner import MissionPlanner
from navigation.core.geometry import GeoPoint

router = APIRouter(tags=["navigation"])
planner = MissionPlanner()


@router.post(
    "/plan-mission",
    response_model=PlanMissionResponse,
    responses={
        200: {"description": "Mission planned successfully"},
        400: {"description": "Invalid polygon or parameters"},
    },
)
def plan_mission(request: PlanMissionRequest) -> dict:
    """Plan a drone mission from a boundary polygon.

    Given a polygon defining the area to cover, calculates:
    - Optimal flight altitude for the desired photo density
    - Boustrophedon (lawnmower) coverage path
    - Camera trigger points along the route
    - Mission statistics (area, time, photos, GSD)
    """
    boundary = [GeoPoint(lat=p.lat, lon=p.lon) for p in request.boundary]

    result = planner.plan_mission(
        boundary_points=boundary,
        photos_per_m2=request.photos_per_m2,
        altitude_m=request.altitude_m,
        overlap_front=request.overlap_front,
        overlap_side=request.overlap_side,
        speed_mps=request.speed_mps,
        margin_m=request.margin_m,
    )

    if "error" in result:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/health")
def health():
    return {"status": "ok"}
