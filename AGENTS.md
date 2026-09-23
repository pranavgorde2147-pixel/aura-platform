# AURA Platform - Agent Instructions

## Repository Structure

Two independent services in this workspace:

| Directory | Purpose | Port | Entry |
|-----------|---------|------|-------|
| `aura-platform/backend/` | FastAPI API server (Postgres, Redis, Qdrant) | 8000 | `app/main.py:create_app()` |
| `server2/` | Internal inference service (Qwen3.5-4B) | 8001 | `app/main.py` |

## Quick Start - Backend

```bash
cd aura-platform/backend
cp .env.example .env  # set real secrets
docker compose up -d  # starts Postgres, Redis, Qdrant
```

Docker healthcheck: `GET /api/v1/health`

## Quick Start - Server 2

```bash
cd server2
cp .env.example .env  # set INTERNAL_API_TOKEN
docker compose up -d  # mounts ~/aura/server2/models/Qwen3.5-4B read-only
```

Health: `GET /health` (returns healthy only after model loads)

## Running Tests

**Server 2 (skip model load):**
```bash
cd server2
.venv/bin/python -m pytest -q tests
```
Tests use `AURA_SKIP_MODEL_LOAD=1` to avoid loading the 8.8 GiB checkpoint.

**Backend:**
```bash
cd aura-platform/backend
.venv/bin/python -m pytest -q tests
```

## Key Constraints

- **Server 2 model**: Qwen3.5-4B only. Mounted read-only from host, never copied into Docker image.
- **AURA_SKIP_MODEL_LOAD**: Set to `1` to skip model loading (used in tests, falls back to external LLM or test response).
- **INTERNAL_API_TOKEN**: Required for Server 2 inference endpoint (`/v1/brain/infer`). Must match between Server 1 and Server 2.
- **Backend infrastructure**: Requires Postgres 16, Redis 7, Qdrant v1.10.1. All have healthchecks in docker-compose.yml.
- **Python 3.14**: Backend Dockerfile uses `python:3.14-slim`.

## Architecture Notes

- Backend API is versioned under `/api/v1` (auth, users, brain, health, identity).
- SQLAlchemy models in `backend/app/models/` use UUID primary keys and timestamped base.
- Alembic migrations in `backend/alembic/`. Run with `alembic upgrade head`.
- Server 2 validates internal bearer token, not user auth. User auth is Server 1's responsibility.
- Server 2 prompt building strips sensitive context keys (vault, password, secret, token, jwt).

## Environment Variables

**Backend** (`aura-platform/backend/.env`):
- `POSTGRES_URL`, `REDIS_URL`, `QDRANT_URL` - infrastructure connections
- `JWT_SECRET_KEY` - change from default in production
- `AI_SERVER_URL` - defaults to `http://localhost:8001` (Server 2)
- `STORAGE_SERVER_URL` - defaults to `http://localhost:9000`

**Server 2** (`server2/.env`):
- `INTERNAL_API_TOKEN` - must match Server 1's token
- `AURA_SKIP_MODEL_LOAD` - `true`/`1` to skip model loading
- `EXTERNAL_AI_URL`, `EXTERNAL_AI_KEY`, `EXTERNAL_MODEL` - for external LLM fallback
