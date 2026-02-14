# ADR 0003: Backpressure and degraded-mode strategy

- Status: Accepted (Phase 0)
- Date: 2026-02-14

## Context
The target platform will run on a single VPS in early phases. Queue spikes, DB saturation, or tool latency regressions can degrade user-facing reliability unless the system has explicit backpressure behavior.

## Decision
Adopt a level-based degraded-mode strategy (L0-L3) driven by measurable signals and configurable thresholds, with priority-aware admission control and recovery gates.

## Signals
- `queue_depth`
- `job_lag_seconds`
- `tool_latency_p95_ms`
- `error_rate_5m`
- `db_saturation`
- `cpu_utilization`
- `ram_utilization`

## Degradation policy
- L0 Normal: standard scheduling.
- L1 Warn: throttle non-critical intake and reduce concurrency.
- L2 Degraded: shed heavy tasks, defer jobs, lower semantic `top_k`, return summary-first + enqueue.
- L3 Critical: reject non-essential work and preserve critical scopes only.

## Priority policy
- P0: `finance:*` and critical task execution.
- P1: docs/memory maintenance.
- P2: experiments and non-essential workloads.

## Recovery policy
Return to normal only after sustained healthy metrics window. Include operator kill switch to force degraded mode during incidents.

## Consequences
### Positive
- Predictable behavior during overload.
- Protects critical flows.
- Faster incident triage due to explicit mode transitions.

### Trade-offs
- More configuration to maintain.
- Risk of over-throttling if thresholds are poorly tuned.

## Verification checklist
- [ ] Mode transitions are observable and auditable
- [ ] P0 traffic is preserved under L2/L3 conditions
- [ ] Recovery requires sustained healthy window
- [ ] Kill switch works and is logged
