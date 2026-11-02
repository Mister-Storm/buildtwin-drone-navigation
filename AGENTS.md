# BuildTwin Drone Navigation — Agent Context

FastAPI service for autonomous drone flight path planning and mission management.

## Cross-agent requirements

Every coding agent MUST read and follow the [canonical BuildTwin constitution](../buildtwin/.specify/memory/constitution.md)
before work. Keep that file canonical; report conflicting guidance rather than inventing exceptions.
Paths and commands below resolve from this repository root.

- Before production edits, record affected journeys, contracts, permissions, data, workers, and
  consumers; distinguish approved behavior, known defects, and unverified behavior.
- Preserve approved legitimate behavior outside scope. Security defects and misleading analytical
  results are not compatibility guarantees. Cite accepted requirements and affected consumers for
  intentional behavior changes; obtain explicit approval for material changes outside scope.
- Reproduce defects with meaningful failing tests where practical; record any reproduction limit.
  Verify positive permitted-success and negative forbidden-action cases. Do not weaken tests to pass.
- Run mandatory repository gates plus impact-appropriate regression, contract, and complete-journey
  acceptance checks, including real browser interactions where required by the constitution.
- Link requirements, implementation, tests, and evidence. Report actual commands, versions, config,
  results, pre-existing failures, and blocked checks. A required blocked check prevents a completion
  claim; builds, health checks, mocks, and HTTP 200 alone do not prove end-to-end correctness.
- Preserve existing data, legitimate ownership, and unrelated working-tree changes. Never reset DBs,
  delete volumes, broaden memberships, disable security, forge tokens, or rewrite job states to pass
  validation. Correct applied migrations through auditable forward migrations.
- Concise status styles must not reduce technical precision, evidence, or disclosure of limitations.

## Repositories

| Repo | Path | Role |
|------|------|------|
| **Drone Navigation** (this repo) | `.` | FastAPI, path planning |
| **Backend API** | `../buildtwin` | Kotlin monolith, consumes this service |

## Quick start

```bash
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
Canonical doc: `../buildtwin/docs/SPRINT-WORKFLOW.md`
Cursor rules: `.cursor/rules/sprint-implementation.mdc`, `.cursor/rules/definition-of-done.mdc`

Conventions (all sprints):
- English-only branches, commits, PRs, identifiers, test names
- No code comments — self-documenting names
- TDD: failing pytest → production code → refactor
- Test subject always named `sut`; test name `test_should_{outcome}_when_{condition}`
- Branch pattern: `{type}/{english-kebab-slug}` from `main`
- Geometry/algorithms in `navigation/core/`; thin routes in `app/api/routes/`
