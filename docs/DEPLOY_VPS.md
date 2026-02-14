# DEPLOY_VPS.md

## Phase 1 baseline (single VPS, OSS)

This phase provisions only:
- PostgreSQL (with pgvector image)
- Redis

Both run in Docker Compose on an internal network with persistent volumes and healthchecks.
No public ports are exposed by default.

## 1) Prerequisites
- Docker Engine + Docker Compose plugin installed
- Access to this repo on the VPS

## 2) Configure environment

```bash
cp .env.example .env
# edit .env and set a strong POSTGRES_PASSWORD
```

### Connectivity mode

Two secure modes are supported:

1. **App in Docker (default)**
   - app reaches `postgres` and `redis` via internal compose network names
   - no host port exposure needed

2. **App on Host (localhost-only port bind)**
   - use compose override to bind ports only to loopback:

```bash
docker compose -f docker-compose.yml -f docker-compose.host.yml up -d
```

This binds Postgres/Redis to `127.0.0.1` only (not public internet).

Required variables:
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

## 3) Start services

```bash
./scripts/dev-up.sh
```

By default this starts postgres + redis only.
Worker can run either:
- host process: `PYTHONPATH=. python3 workers/jobs_worker.py`
- compose profile: `docker compose --profile workers up -d worker`

## 4) Verify health

```bash
docker compose ps
docker compose logs --tail=50 postgres
docker compose logs --tail=50 redis
```

Expected:
- postgres status `healthy`
- redis status `healthy`

## 5) Smoke tests

### Full DB smoke (recommended)
```bash
./scripts/smoke-db.sh
```

### Queue/worker smoke (Phase 4)
```bash
./scripts/test-jobs.sh
```

### Observability smoke (Phase 5)
```bash
./scripts/test-observability.sh
```

### Manual quick checks
```bash
docker compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT version();"
docker compose exec redis redis-cli ping
```
Expected Redis output: `PONG`

## 6) Stop services

```bash
./scripts/dev-down.sh
```

## Security defaults in this phase
- No `ports:` published in compose (internal network only)
- Credentials loaded from `.env`
- Minimal service surface (Postgres + Redis only)

## Docs check

```bash
./docs_check 1
```
