# DASHBOARD Scope A — Premium Runtime Spec

## Purpose
Define a strict, low-noise runtime contract for `#sistema` snapshots.
Only real execution state is published.

## Canonical Runtime Blocks (exact names)
Each snapshot **must** include these four top-level blocks in this exact order:

### ACTIVE_NOW
Work currently executing.
- Include only tasks with active owner + active execution evidence.
- Max 3 items.
- Required item fields: `id`, `owner`, `task`, `started_at`, `evidence`.

### BLOCKED
Work halted by external dependency.
- Include only blockers requiring action.
- Required item fields: `id`, `owner`, `blocked_by`, `since`, `unblock_action`.

### DONE
Recently completed work with proof.
- Include only items completed since previous snapshot.
- Required item fields: `id`, `owner`, `result`, `completed_at`, `evidence`.

### NEXT_TRIGGER
What should start next and under what condition.
- Include immediate executable triggers only.
- Required item fields: `id`, `trigger_condition`, `next_action`, `owner`.

## Quality Rules (premium)
1. **Truth over optimism**: never mark work active without concrete runtime evidence.
2. **No ambiguity**: avoid labels like “in progress” unless represented in `ACTIVE_NOW` with timestamps.
3. **Signal-only output**: if all blocks are empty/no material change, emit `NO_REPLY`.
4. **Evidence required**: every `ACTIVE_NOW` and `DONE` item must include verifiable evidence (commit, file path, command output, message link).
5. **Scope separation**: strategic planning docs are not runtime state; runtime state lives in `runtime/RUNTIME_STATE.json`.
6. **Deterministic format**: block names and field names are fixed; no ad-hoc keys in snapshots.
7. **Freshness**: snapshots must include `generated_at` and source revision/hash.

## Snapshot Output Contract for #sistema
Snapshots are rendered from runtime truth and must follow this section order:
1. Header (`generated_at`, `source_rev`)
2. `ACTIVE_NOW`
3. `BLOCKED`
4. `DONE`
5. `NEXT_TRIGGER`

No additional narrative unless a blocker escalation is required.
