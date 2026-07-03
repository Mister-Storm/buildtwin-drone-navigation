"""BuildTwin Drone Navigation Service — FastAPI application."""

from fastapi import FastAPI

from app.api.routes import navigation

app = FastAPI(
    title="BuildTwin Drone Navigation",
    description="Path planning and mission management for autonomous drone flights",
    version="0.1.0",
)

app.include_router(navigation.router)
