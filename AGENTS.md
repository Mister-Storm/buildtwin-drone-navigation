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

## Quality gates

Before any PR merge:
1. `ruff check .` — lint
2. `python -m pytest tests/ -v` — all tests green
3. CI coverage: 70% on `app` + `navigation`

## Sprint workflow

Skill: `~/.cursor/skills/buildtwin-sprint/SKILL.md`
Canonical doc: `../BuildTwin/docs/SPRINT-WORKFLOW.md`
Cursor rules: `.cursor/rules/sprint-implementation.mdc`, `.cursor/rules/definition-of-done.mdc`

Conventions (all sprints):
- English-only branches, commits, PRs, identifiers, test names
- No code comments — self-documenting names
- TDD: failing pytest → production code → refactor
- Test subject always named `sut`; test name `test_should_{outcome}_when_{condition}`
- Branch pattern: `{type}/{english-kebab-slug}` from `main`
- Geometry/algorithms in `navigation/core/`; thin routes in `app/api/routes/`
