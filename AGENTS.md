# BuildTwin Drone Navigation — Agent Context

FastAPI service for autonomous drone flight path planning and mission management.

## Repositories

| Repo | Path | Role |
|------|------|------|
| **Drone Navigation** (this repo) | `/home/mister-storm/development/buildtwin-drone-navigation` | FastAPI, path planning |
| **Backend API** | `/home/mister-storm/development/BuildTwin` | Kotlin monolith, consumes this service |

## Quick start

```bash
cd /home/mister-storm/development/buildtwin-drone-navigation
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8091
```

## Architecture

```
app/
  main.py          — FastAPI app
  api/routes/      — REST endpoints
  models/          — Pydantic schemas
  services/        — Business logic (coverage_planner)
navigation/        — Core geometry library (GeoPoint, path algorithms)
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check → `{"status":"ok"}` |
| POST | `/plan-mission` | Plan drone mission from boundary polygon |

### POST /plan-mission

Request:
```json
{
  "boundary": [{"lat": -23.55, "lon": -46.63}, ...],
  "photos_per_m2": 0.1,
  "altitude_m": 80,
  "overlap_front": 0.75,
  "overlap_side": 0.60,
  "speed_mps": 10,
  "margin_m": 10
}
```

Response: waypoints, area, estimated time, photo count, GSD.

## Production

- Runs as Docker container in the `buildtwin-net` network
- Consumed by the Kotlin backend via `http://drone-navigation:8091`
- No public UI — API-only service
