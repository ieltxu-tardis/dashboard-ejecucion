# SCOPE_A_RUNTIME_EVENTS.md

Defines when Scope A should emit runtime events to `#agent-feed`.

## Channel
- Destination: `#agent-feed`
- Principle: emit only on **real execution state changes** (no timer-only noise).

## Event contract

### STARTED
Emit when work on a concrete task actually begins.

Required conditions:
- Task moved from not-in-progress to in-progress.
- `runtime/RUNTIME_STATE.json` reflects new ACTIVE item (or ACTIVE item start metadata).

Do not emit when:
- Reposting status with no state transition.
- Editing wording only.

Minimum payload:
- `event=STARTED`
- `task_id`
- `owner`
- `started_at`
- `evidence_path` (if available)

---

### HEARTBEAT
Emit only when there is **material runtime progress** while task remains active.

Required conditions (at least one):
- New evidence artifact created/updated and tied to active task.
- Meaningful %/milestone jump (not cosmetic text edits).
- Blocker cleared and execution resumed.

Rate rule:
- Event-driven only; no fixed-interval heartbeat.

Minimum payload:
- `event=HEARTBEAT`
- `task_id`
- `progress_delta`
- `evidence_path` (or explicit change summary)
- `timestamp`

---

### BLOCKED
Emit when execution cannot continue due to an external dependency or hard failure.

Required conditions:
- Task transitions to blocked state.
- Blocker is concrete and actionable.

Minimum payload:
- `event=BLOCKED`
- `task_id`
- `blocked_by`
- `since`
- `unblock_action`
- `owner`

Update rule:
- Re-emit BLOCKED only if blocker meaningfully changes.

---

### COMPLETED
Emit when task is actually done with evidence.

Required conditions:
- Task leaves ACTIVE and enters DONE.
- Output artifact(s) or commit evidence exists.

Minimum payload:
- `event=COMPLETED`
- `task_id`
- `result`
- `completed_at`
- `evidence_path` (file path and/or commit hash)

## Mapping to runtime truth
Each emitted event should correspond to a real edit in `runtime/RUNTIME_STATE.json`:
- STARTED -> ACTIVE_NOW add/update
- HEARTBEAT -> ACTIVE_NOW progress/evidence update
- BLOCKED -> BLOCKED add/update
- COMPLETED -> DONE add/update (+ removal from ACTIVE_NOW when applicable)

## Anti-noise guard
If no material runtime change occurred, do not emit to `#agent-feed`.
Use `NO_REPLY` semantics in snapshot publishing to avoid duplicate chatter.
