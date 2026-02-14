# JOBS_QUEUE.md

## Phase 4 queue/workers baseline

## Stack choice
- Redis Streams + consumer group (`jobs:stream`, group `workers`)
- In-repo Python worker (`workers/jobs_worker.py`)
- DB-backed state (`jobs`, `job_runs`) as source of truth

Runtime mode in this phase:
- default tests run worker on host process (`PYTHONPATH=. python3 workers/jobs_worker.py`)
- optional compose worker profile is available (`--profile workers`)

## Job types
- `embed_document`
- `summarize_period`
- `memory_compact` (placeholder noop in Phase 4)

## Idempotency
- `jobs.dedupe_key` unique per tenant (`UNIQUE (tenant_id, dedupe_key)`).
- Queue layer dedupes before enqueue if existing status is queued/running/done.

## Retries/backoff
- `attempts`, `max_attempts` on job row.
- Exponential backoff via `compute_backoff_seconds`.
- On failure: status reverts to `queued` with delayed `scheduled_at`, or `failed` if max attempts reached.

## Timeouts/budgets
- Per-job `timeout_seconds` persisted.
- Embedding worker budget:
  - `JOB_MAX_CHUNKS_PER_DOC` (default 128)
- Enqueue budget:
  - `max_jobs_per_request` in queue config

## Tenant safety
- Every job row has `tenant_id`.
- Worker handlers always query/write with tenant-scoped predicates.

## Minimal runtime signals
- Worker emits JSON lines (stdout):
  - `worker_started`
  - `job_done`
  - `job_failed`

## Rollback
- Stop worker process/container.
- Keep schema; async path can be disabled while preserving core MemoryService writes/reads.
