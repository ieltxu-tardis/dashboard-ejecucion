# ROADMAP.md

## Phase plan (incremental, PR-sized)

## Phase 0 — Discovery + Plan + ADR (this delivery)
- Inspect repos and integration seams.
- Produce architecture docs and initial ADR.
- No code implementation beyond docs.

## Phase 1 — Infrastructure baseline (single VPS, OSS)
Deliverables:
- `docker-compose.yml` (Postgres + pgvector, Redis, optional Prometheus/Grafana)
- `.env.example`
- `scripts/dev-up.sh`, `scripts/dev-down.sh`
- `docs/DEPLOY_VPS.md`

Acceptance:
- `docker compose up -d` healthy
- no secrets in repo

## Phase 2 — DB schema + migrations (multi-tenant memory core)
Deliverables:
- migration framework wired
- core tables with `tenant_id`
- pgvector-enabled embeddings table
- seed (default tenant/user)
- dedupe on `documents.content_hash`

Acceptance:
- clean migration on empty DB
- rollback path documented

## Phase 3 — Memory Service contracts + adapters
Deliverables:
- memory API contract (`write/read/semantic/episodic/audit`)
- policy-gated writes
- tenant-filtered reads
- integration tests for one write/read path

Acceptance:
- docs/API_MEMORY.md complete
- tests passing

## Phase 4 — Queue + workers
Deliverables:
- Redis-backed jobs
- workers for embeddings, summaries, compaction
- idempotency + retry/backoff
- queue/job metrics

Acceptance:
- enqueue and process path verified

## Phase 5 — Observability baseline
Deliverables:
- structured JSON logs
- `/metrics` endpoint with core counters/histograms
- optional tracing skeleton
- docs/OBSERVABILITY.md + runbook

Acceptance:
- metrics scrape works
- baseline dashboard/alerts documented

## Phase 6 — Policy engine + governance
Deliverables:
- scope checks per action
- request budgets
- approval gates for sensitive ops
- audit log schema + redaction rules

Acceptance:
- policy decisions testable and auditable

---

## Milestones and stop points

```yaml
milestones:
  M0_discovery_docs: done_in_phase_0
  M1_infra_healthy: phase_1
  M2_schema_live: phase_2
  M3_memory_contract_live: phase_3
  M4_async_jobs_live: phase_4
  M5_observability_live: phase_5
  M6_policy_live: phase_6
```

## Risk ledger (initial)

```yaml
risks:
  - id: R1
    name: schema_lock_in
    mitigation: adr + migration discipline + adapter boundaries
  - id: R2
    name: observability_afterthought
    mitigation: phase_5 mandatory before broad feature expansion
  - id: R3
    name: multi-tenant retrofit pain
    mitigation: tenant_id from first migration set
  - id: R4
    name: queue complexity drift
    mitigation: minimal job types first, strict idempotency
```
