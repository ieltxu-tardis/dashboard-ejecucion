# ADR 0002: ToolRunner boundaries and execution contract

- Status: Accepted (Phase 0)
- Date: 2026-02-14

## Context
Phase 1 will introduce runtime components. Without explicit boundaries between Orchestrator and ToolRunner, tool execution may bypass policy, budgets, or audit requirements.

## Decision
Define ToolRunner as a separate execution module with contract-first interfaces and explicit sandbox/resource/network/filesystem controls.

## Decision drivers
- Keep orchestration logic separate from tool runtime concerns.
- Make approval and policy checks testable.
- Standardize tool metadata so execution is deterministic and auditable.

## Responsibilities
- Orchestrator: planning, policy pre-checks, budget checks, lifecycle decisions.
- ToolRunner: sandboxed execution, limits enforcement, event streaming, execution result packaging.

## Tool contract requirements
Required fields per tool:
- `name`
- `scope`
- `input_schema`
- `output_schema`
- `max_runtime_seconds`
- `network_policy`
- `fs_policy`
- `requires_approval`

## Consequences
### Positive
- Reduced ambiguity in ownership.
- Easier test coverage for approval, timeout, and policy paths.
- Better incident forensics via consistent execution metadata.

### Trade-offs
- More upfront schema and registry discipline.
- Requires strict backward compatibility for contract versions.

## Observability and audit requirements
Every execution event must include `tenant_id`, `request_id`, `trace_id`, `tool_call_id`, and status transitions. Long-running executions must emit heartbeats.

## Verification checklist
- [ ] Contract schemas validated in CI
- [ ] Policy checks occur before ToolRunner dispatch
- [ ] Timeout/resource controls enforced by ToolRunner
- [ ] Audit events present for success/failure/deny/timeout
