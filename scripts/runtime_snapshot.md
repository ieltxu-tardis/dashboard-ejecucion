# Runtime Snapshot Generation (`#sistema`)

## Objective
Generate deterministic `#sistema` snapshots from runtime truth in `runtime/RUNTIME_STATE.json`.

## Source of Truth
- Primary input: `runtime/RUNTIME_STATE.json`
- Required top-level blocks (exact):
  - `ACTIVE_NOW`
  - `BLOCKED`
  - `DONE`
  - `NEXT_TRIGGER`

## Generation Rules
1. Read `generated_at` and `source_rev` for snapshot header.
2. Render blocks in strict order:
   1) `ACTIVE_NOW`
   2) `BLOCKED`
   3) `DONE`
   4) `NEXT_TRIGGER`
3. Preserve item field names exactly as stored in runtime state.
4. Do not inject planning/speculation text.
5. If no meaningful changes since last published snapshot and all signal is empty, output `NO_REPLY`.

## Validation Checklist
Before posting to `#sistema`, verify:
- Block names are exact and present.
- Every `ACTIVE_NOW` and `DONE` item has `evidence`.
- Every `BLOCKED` item has a concrete `unblock_action`.
- Every `NEXT_TRIGGER` item is actionable and assigned.

## Minimal Snapshot Template
```text
#sistema snapshot
generated_at: <ISO8601>
source_rev: <hash/rev>

ACTIVE_NOW
- ...

BLOCKED
- ...

DONE
- ...

NEXT_TRIGGER
- ...
```
