# RUNBOOK.md

## Quick diagnostics

### Stack health
```bash
docker compose ps
docker compose logs --tail=80 postgres
docker compose logs --tail=80 redis
```

### DB migrations + seed
```bash
./scripts/db-migrate.sh
./scripts/db-seed.sh
```

### Jobs pipeline
```bash
./scripts/test-jobs.sh
```

### Observability smoke
```bash
./scripts/test-observability.sh
```

## Incident playbooks

### API/Memory slow
1. Check metrics endpoint (`/metrics`) for latency and queue depth.
2. Check queued jobs:
```bash
python3 - <<'PY'
from memory_service.db import PostgresExec
print(PostgresExec().fetchone_value("SELECT COUNT(*)::text FROM jobs WHERE status='queued'"))
PY
```
3. If queue high, pause heavy ingest and process backlog.

### Jobs stuck
1. Inspect running/failed jobs:
```bash
python3 - <<'PY'
from memory_service.db import PostgresExec
print(PostgresExec().fetchall_json("SELECT id::text,type,status,attempts,last_error FROM jobs ORDER BY updated_at DESC LIMIT 20"))
PY
```
2. Restart worker process.
3. Re-run `./scripts/test-jobs.sh`.

### Approval stuck
1. Inspect pending approvals:
```bash
python3 - <<'PY'
from memory_service.db import PostgresExec
print(PostgresExec().fetchall_json("SELECT id::text,actor_ref,action,scope,status,created_at FROM approval_requests WHERE status='pending' ORDER BY created_at DESC LIMIT 20"))
PY
```
2. Verify actor scopes and tool registry metadata.
3. Decide approve/reject path (manual until approval API is added).

### Budget exhausted
1. Check recent governance denies:
```bash
python3 - <<'PY'
from memory_service.db import PostgresExec
print(PostgresExec().fetchall_json("SELECT created_at,error_code,route FROM observability_events WHERE component='governance' ORDER BY created_at DESC LIMIT 30"))
PY
```
2. Adjust env budgets only if justified.
3. Re-test with `./scripts/test-governance.sh`.

### Safe mode active unexpectedly
1. Check env flags (`SAFE_MODE_*`).
2. Set to `0` and restart relevant processes.
3. Confirm policy decisions return to expected allow/deny mix.

### Redis down
1. Check container logs.
2. Restart redis service.
3. Re-run queue smoke.

### Embeddings not appearing
1. Confirm `embed_document` jobs are queued/running/done.
2. Confirm worker is running.
3. Check `document_chunks` and `embeddings` counts for tenant/doc.

### DB locks/errors
1. Check pg_stat_activity and lock waits.
2. Identify long transactions.
3. Apply controlled restart only if needed.
