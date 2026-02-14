# ARCHITECTURE.md

## Phase 0 — Discovery Snapshot (2026-02-14)

## 1) Current repository topology

```text
/root/.openclaw/workspace                 # repo: dashboard-ejecucion (gh-pages)
├─ bridge/remote                          # repo: openclaw-bridge (main)
├─ system-core                            # repo: tardis-system-core (master)
├─ foundation-inputs                      # incoming docs/prompts
├─ memory + MEMORY.md                     # fresh baseline after nuclear reset
└─ _nuclear_reset / _trash                # archived prior state
```

### Observations
- Root repo is currently acting as orchestration/documentation shell, not an application runtime.
- `system-core` holds operational conventions and prior architecture intent.
- `bridge/remote` appears to be a separate dashboard/integration artifact repository.
- Runtime services for memory/queue/observability are **not yet implemented** in the root workspace.

## 2) Existing operational seams (integration points)

### Orchestrator seam
- OpenClaw runtime is external to this repo, but this workspace is used as control-plane files.
- Best insertion point: create internal service boundaries via docs + adapters first (Phase 1+).

### Memory seam
- Existing: flat files (`MEMORY.md`, `memory/*.md`).
- Target seam: Memory Service API (structured + semantic + episodic), with file-memory as fallback adapter.

### Jobs seam
- Existing: no active cron/jobs after reset.
- Target seam: queue-backed jobs (embeddings, summarize, compaction) with idempotent workers.

### Observability seam
- Existing: ad-hoc textual updates, no stable metrics endpoint in this workspace.
- Target seam: JSON logs + Prometheus metrics + optional OTel tracing.

## 3) Target architecture (modular, single-VPS OSS)

### Layered model
1. **Control Plane**
   - policy engine, orchestration rules, approval gates, audit trail
2. **Memory Plane**
   - Postgres (truth) + pgvector (semantic retrieval)
3. **Execution Plane**
   - stateless API + Redis queue + workers
4. **Observability Plane**
   - logs, metrics, traces, runbooks

### Data boundaries
- Every data-bearing table scoped by `tenant_id` from day one.
- Memory writes require explicit policy gating and source attribution.

## 4) Contract-first policy baseline (structured)

```yaml
policy_baseline_v0:
  scope_model:
    - finance:read
    - finance:write
    - docs:ingest
    - memory:write
    - exec:sandbox
  write_policy:
    allowed_when:
      - explicit_user_intent
      - explicit_command
      - validated_structured_extraction
    required_fields:
      - tenant_id
      - source
      - confidence
      - audit_ref
  request_budget:
    max_tool_calls: 12
    max_runtime_seconds: 120
    max_jobs_enqueued: 5
  approvals:
    required_for:
      - destructive_file_ops
      - external_side_effects
      - privilege_boundary_changes
```

## 5) Phase 0 conclusion
- Discovery complete.
- Architecture direction selected: Postgres + pgvector + Redis, modularized behind service contracts.
- No runtime code changes performed in this phase.
