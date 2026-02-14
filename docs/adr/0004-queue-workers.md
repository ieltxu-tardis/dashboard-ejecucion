# ADR 0004: Queue + Workers with Redis Streams (custom lightweight worker)

- Status: Accepted (Phase 4)
- Date: 2026-02-14

## Context
We need async job execution for embeddings and summaries, with tenant-safe idempotency, retries, and backoff. The repo currently has no established queue framework.

## Decision
Use **Redis Streams + consumer group** with a lightweight in-repo Python worker.

## Why this option
- Uses existing Redis infra already in compose.
- No heavy framework dependency.
- Explicit control over idempotency, retries, and backoff logic.
- Easy to audit job lifecycle in DB (`jobs`, `job_runs`).

## Trade-offs
- More custom code than adopting RQ/Dramatiq.
- Requires clear docs and test coverage to avoid drift.

## Consequences
- Jobs are enqueued in DB + Redis stream.
- Worker claims stream messages and executes handlers.
- Retries and failures are tracked in DB and `job_runs`.

## Rollback path
- Stop worker service.
- Keep DB schema; async path can be disabled by env flag.
- Continue using synchronous reads and no async enrichment.
