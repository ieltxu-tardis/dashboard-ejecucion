# SCOPE_A_MESSAGE_STYLE.md

Message style contract for Scope A channel outputs.

## Goals
- Human-readable in one glance
- Compact (short lines, no noisy metadata)
- High-signal updates tied to runtime truth
- No `key=value` machine payloads in channel-facing text

## Channels
- `#sistema`: periodic runtime snapshot (4 blocks)
- `#agent-feed`: event-driven execution events (`STARTED`, `HEARTBEAT`, `BLOCKED`, `COMPLETED`)

---

## `#sistema` template (snapshot)

Use this structure:

```md
## Scope A Runtime Snapshot
Updated: <generated_at> · Marker: <material_change_marker>

### Active now
- <id> · <owner> — <task>
- ...

### Blocked
- <id> · <owner> — <blocked_by>
  ↳ Unblock: <unblock_action>

### Done
- <id> · <owner> — <result>
  ↳ Evidence: <evidence>

### Next trigger
- <id> · <owner> — <next_action>
  ↳ Condition: <trigger_condition>
```

Rules:
- Max 3 bullets per section (append `… (+N more)` if needed).
- If empty, print `- none`.
- Keep evidence and unblock hints in sub-lines (`↳`) for readability.
- Avoid raw JSON or key-value dumps.

---

## `#agent-feed` template (events)

### STARTED
```md
▶️ STARTED · <task_id>
Owner: <owner>
Started: <started_at>
Evidence: <evidence_path>
```

### HEARTBEAT
```md
💓 HEARTBEAT · <task_id>
Progress: <progress_delta>
Evidence: <evidence_path>
Time: <timestamp>
```

### BLOCKED
```md
⛔ BLOCKED · <task_id>
Owner: <owner>
Why: <blocked_by>
Since: <since>
Unblock: <unblock_action>
```

### COMPLETED
```md
✅ COMPLETED · <task_id>
Result: <result>
Completed: <completed_at>
Evidence: <evidence_path>
```

Rules:
- Emit only on material change.
- One event per runtime tick.
- Keep to 4–5 short lines.
- No `event=... task_id=...` machine format.
