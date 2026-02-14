# WORK_PUMP

Purpose: transform every user intention into motion (ACTIVE_NOW) or explicit parking (BLOCKED) with reason.

## Core Rule

Every incoming intention must end this cycle in exactly one bucket:

1. **ACTIVE_NOW** (doing now), or
2. **BLOCKED** (parked with reason + trigger), or
3. **DONE** (already satisfied/closed).

No silent backlog, no undefined waiting.

## Intake-to-Execution Pump

1. **Capture**
   - Convert user message into a single clear task statement.

2. **Qualify**
   - Check: is there enough info/tools/authority to move now?

3. **Route**
   - If yes: create/update task as **ACTIVE_NOW** with next action.
   - If no: create/update task as **BLOCKED** with:
     - blocker reason,
     - unblock trigger,
     - fallback action + review time.

4. **Drive**
   - Execute next action for ACTIVE_NOW.
   - After each action, either:
     - continue ACTIVE_NOW with next step,
     - move to BLOCKED (with explicit reason), or
     - mark DONE.

5. **Recover from Drift**
   - If no ACTIVE_NOW exists at any checkpoint, promote highest-priority actionable task immediately.
   - If only BLOCKED tasks exist, run fallback/escalation actions at trigger times.

## Parking Standard (Explicit, Never Implicit)

A parked task is valid only if it records all of:

- Why it is blocked (specific dependency)
- What event unblocks it (message, approval, time, artifact)
- When to re-check
- What to do if trigger does not occur

If any field is missing, it is not parked correctly and must be fixed in the same cycle.

## Anti-Idle Guarantees

- At cycle end: at least one of {ACTIVE_NOW exists, escalation/fallback scheduled} is true.
- BLOCKED items always have a next observation point.
- DONE is terminal; no hidden reopen without a new intention.

## Minimal Data Model

For each task track:

- `state`: ACTIVE_NOW | BLOCKED | DONE
- `next_action`: string (required for ACTIVE_NOW)
- `blocker_reason`: string (required for BLOCKED)
- `unblock_trigger`: string (required for BLOCKED)
- `review_at`: timestamp (required for BLOCKED)
- `closure_note`: string (required for DONE)
