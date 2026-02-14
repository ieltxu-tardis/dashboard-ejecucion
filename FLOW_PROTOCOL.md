# FLOW_PROTOCOL

Purpose: keep execution continuously moving; no idle/dead state. Every tracked item must be in exactly one of three states.

## States (only these)

- **ACTIVE_NOW**
  - Definition: currently executable work with an identified next action.
  - Required fields: owner, next action, due/checkpoint time.

- **BLOCKED**
  - Definition: cannot progress right now due to an external dependency or missing input.
  - Required fields: blocker reason, unblock trigger, fallback action (if trigger misses).

- **DONE**
  - Definition: objective complete or intentionally closed.
  - Required fields: completion note (or closure reason), timestamp.

## Trigger Rules

### Enter ACTIVE_NOW when
- A new user intention arrives and is actionable.
- A BLOCKED item receives its unblock trigger.
- ACTIVE_NOW checkpoint expires without completion (re-affirm and continue with next concrete step).

### Leave ACTIVE_NOW to BLOCKED when
- Progress requires external input/approval/resource not available now.
- Retry budget is exhausted and waiting is the fastest path.

### Leave ACTIVE_NOW to DONE when
- Acceptance criteria are met and output delivered.
- User explicitly cancels/closes the task.

### Leave BLOCKED to ACTIVE_NOW when
- Required input arrives.
- Timeout trigger fires and fallback action is available.

### Leave BLOCKED to DONE when
- User cancels, supersedes, or declares no further action needed.

## Invariants

- No task exists without state.
- No task may remain BLOCKED without an explicit unblock trigger.
- No task may remain ACTIVE_NOW without a next action.
- If no ACTIVE_NOW exists, immediately promote the highest-priority actionable item from queue/park.
- No operational channel is considered DONE unless it is instrumented and emitting verifiable runtime signal.

## Operational Channel Guardrail (mandatory)

When creating or accepting an operational channel (e.g., `#sistema`, `#agent-feed`), completion requires all of the following:

1. Channel created.
2. Runtime telemetry connected.
3. State semantics defined (strategy vs runtime).
4. Anti-noise rule active (`NO_REPLY` when no meaningful change).
5. One pinned usage note with expected event format.

**Definition of Done for channel setup:**
`created + instrumented + semantics + anti-noise + pinned guide`.

Anything less is `IN_PROGRESS`, not `DONE`.

## Operator Loop Checklist (max 8)

- Capture latest user intention as a task candidate.
- If actionable now, set **ACTIVE_NOW** with one concrete next action.
- If not actionable, set **BLOCKED** with explicit reason + unblock trigger.
- Ensure exactly one current next action is owned and time-bounded.
- Execute/update; after each step, re-evaluate state.
- On blocker timeout, run fallback or escalate for input.
- Mark **DONE** only with completion/closure note.
- If ACTIVE_NOW is empty, pull next actionable item immediately.
