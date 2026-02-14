# ARCHITECTURE.md

## Phase 0 - Discovery Snapshot (2026-02-14)

## 1) Current repository topology

```text
/root/.openclaw/workspace                 # repo: dashboard-ejecucion (gh-pages)
|- bridge/remote                          # repo: openclaw-bridge (main)
|- system-core                            # repo: tardis-system-core (master)
|- foundation-inputs                      # incoming docs/prompts
|- memory + MEMORY.md                     # fresh baseline after nuclear reset
`- _nuclear_reset / _trash                # archived prior state
```

### Observations
- Root repo is currently acting as orchestration/documentation shell, not an application runtime.
- `system-core` holds operational conventions and prior architecture intent.
- `bridge/remote` appears to be a separate dashboard/integration artifact repository.
- Runtime services for memory/queue/observability are not yet implemented in the root workspace.

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

### Policy seam
- Existing: implicit policy behavior.
- Target seam: explicit scope checks, approval gates, and request budgets enforced before tool execution.

## 3) Target architecture (modular, single-VPS OSS)

### Layered model
1. **Control Plane**
   - policy engine, orchestration rules, approval gates, audit trail
2. **Memory Plane**
   - Postgres (truth) + pgvector (semantic retrieval)
3. **Execution Plane**
   - Orchestrator + ToolRunner + Redis queue + workers
4. **Observability Plane**
   - logs, metrics, traces, runbooks

### Core module boundaries

| Module | Responsibilities | Out of scope |
|---|---|---|
| Orchestrator | Accept request, plan tool calls, enforce policy pre-checks, decide sync vs async, own request lifecycle | Running tool process directly, raw DB writes for memory |
| ToolRunner / Execution Plane | Execute tool calls in sandbox, enforce timeout/resource/egress/fs policy, emit execution events | Policy decisions, product-level orchestration |
| MemoryService | Write/read structured memory, semantic search, episodic summaries, audit-linked writes | Direct tool execution |
| Workers | Async jobs (embeddings/summaries/compaction), retries/backoff, idempotent processors | User-facing orchestration |
| Policy Engine | Scope checks, approval gates, request budgets, redaction policy | Running tools or DB migrations |

### Memory layers
- Structured memory: transactional records for facts, entities, and policy/audit metadata.
- Semantic memory: vector index for retrieval (`pgvector`) constrained by tenant scope.
- Episodic memory: distilled summaries linked to source events and confidence.

### Data boundaries
- Every data-bearing table scoped by `tenant_id` from day one.
- Memory writes require explicit policy gating and source attribution.
- Cross-tenant reads/writes are denied by default.

## 4) ToolRunner / Execution Plane contract

### Responsibilities and hard limits
- Sandbox execution profile per tool (`sandbox_profile`: strict/default/privileged).
- Timeout control (`max_runtime_seconds`) enforced by ToolRunner and validated by Orchestrator.
- Resource limits per invocation (`cpu_limit`, `memory_limit_mb`, optional `io_limit`).
- Network egress policy (`network_policy`: none/internal/allowlist/all).
- Filesystem policy (`fs_policy`: read-only/read-write/path allowlist).
- Approval interception when `requires_approval=true` before side effects.

### Minimal interface: Orchestrator <-> ToolRunner

**ExecutionRequest (Orchestrator -> ToolRunner)**

```yaml
execution_request_v1:
  request_id: string
  trace_id: string
  tenant_id: string
  actor_id: string
  scope: string
  tool_name: string
  tool_version: string
  input: object
  timeout_seconds: integer
  priority: P0|P1|P2
  requires_approval: boolean
  approval_ref: string|null
  budget_ref: string
```

**ExecutionResult (ToolRunner -> Orchestrator)**

```yaml
execution_result_v1:
  request_id: string
  trace_id: string
  tool_call_id: string
  status: success|failed|timed_out|denied|deferred
  output: object|null
  error_code: string|null
  error_summary: string|null
  started_at: timestamp
  finished_at: timestamp
  runtime_ms: integer
  resource_usage:
    cpu_ms: integer
    peak_memory_mb: integer
  audit_ref: string
```

### Tool registry / contract metadata
Each tool must declare at least:
- `name`
- `scope`
- `input_schema`
- `output_schema`
- `max_runtime_seconds`
- `network_policy`
- `fs_policy`
- `requires_approval`

Recommended additional metadata:
- `version`, `owner`, `idempotent`, `side_effect_level`, `default_priority`, `retry_policy`.

### Tool registration, execution, and audit flow
1. Tool definition is registered in a versioned registry file (YAML/JSON) and schema-validated in CI.
2. Orchestrator resolves tool metadata and runs policy + budget checks.
3. If approved, Orchestrator sends `ExecutionRequest` to ToolRunner.
4. ToolRunner executes in sandbox and streams execution events.
5. Orchestrator records outcome, updates memory/audit records, and returns response.

Audit requirements:
- Every invocation writes audit event(s) with `tenant_id`, `request_id`, `trace_id`, `tool_call_id`, `scope`, decision, and outcome.
- Denied/timeout/deferred outcomes are audited with reason code.

### Observability contract (heartbeats + trace_id/request_id)
- Every tool execution event must include: `request_id`, `trace_id`, `tool_call_id`, `tenant_id`, `scope`, `status`.
- ToolRunner sends heartbeat events at fixed interval (`heartbeat_interval_seconds`, default 5s) while running long calls.
- Heartbeat and status events feed both logs and metrics (`tool_running`, `tool_timeout_total`, `tool_error_total`, `tool_runtime_ms`).
- Lost heartbeats over `heartbeat_miss_threshold` trigger degraded-mode evaluation and optional cancellation policy.

## 5) Backpressure & Degraded Mode

### Primary signals
- `queue_depth` (pending jobs)
- `job_lag_seconds` (oldest job age)
- `tool_latency_p95_ms` (interactive path)
- `error_rate_5m` (execution + infra errors)
- `db_saturation` (connections/lock wait/p95 query latency)
- `cpu_utilization` and `ram_utilization`

### Initial thresholds (configurable defaults)

```yaml
degraded_thresholds_v1:
  warn:
    queue_depth: 100
    job_lag_seconds: 60
    tool_latency_p95_ms: 3000
    error_rate_5m: 0.05
    cpu_utilization: 0.75
    ram_utilization: 0.80
  critical:
    queue_depth: 300
    job_lag_seconds: 180
    tool_latency_p95_ms: 7000
    error_rate_5m: 0.12
    cpu_utilization: 0.90
    ram_utilization: 0.92
```

### Degradation actions by level
- L0 Normal: standard execution.
- L1 Warn: throttle new non-critical requests, reduce concurrency.
- L2 Degraded: shed heavy tasks, defer async jobs, reduce retrieval `top_k`, return summary-first response + enqueue full job.
- L3 Critical: reject non-essential actions, allow only high-priority scopes, enforce strict timeouts and lower budgets.

Supported actions:
- Throttle request admission.
- Shed expensive tasks (batch embeddings/re-index/large summarization).
- Defer low-priority jobs to queue.
- Reduce semantic retrieval depth (`top_k`, context window).
- Reply with short actionable summary + background enqueue for completion.
- Reject non-essential operations while preserving critical flows.

### Priority policy by scope
- P0: `finance:*`, high-value task execution, policy/audit writes.
- P1: docs ingestion, memory compaction, standard analytics.
- P2: experiments, games, exploratory workloads.

Backpressure decisions must preserve P0 first, then P1, and shed/defer P2 earliest.

### Recovery, kill switch, and SLO alignment
- Recovery to normal requires thresholds below `warn` for a sustained window (default 10 minutes).
- Kill switch: force degraded mode with `DEGRADED_MODE_FORCE=true` for incident control.
- Exit switch: `DEGRADED_MODE_FORCE=false` only after operator verification.

Baseline SLO targets:
- Interactive tool path p95 < 4s in normal mode.
- Queue lag p95 < 120s in normal mode.
- Error rate < 2% rolling 15m in normal mode.

## 6) Contract-first policy baseline (structured)

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

## 7) Phase 3 interface update
- `memory_service/` now contains `IMemoryService` + `PostgresMemoryService`.
- Write path is policy-gated (`WritePolicyEngine`) and schema-validated before persistence.
- Read path enforces tenant filtering in all structured queries.
- Semantic search contract is live (`semantic_search`) and compatible with deferred embedding generation.

## 8) Status snapshot
- Discovery and infra baseline complete.
- DB schema/migrations in place.
- Memory Service baseline implemented (structured reads/writes + audit + semantic query interface).
