# DASHBOARD_SCOPE_A.md

## Decision
Dashboard v1 = **Scope A (Lean, high quality)**.

## Official Surfaces
- `#sistema` → executive runtime snapshot (source of truth)
- `#agent-feed` → event-level trace and handoffs

## v1 Required Blocks (in #sistema)
1. `ACTIVE_NOW` (only real running work)
2. `BLOCKED` (only blockers needing action)
3. `DONE` (recent completions with evidence)
4. `NEXT_TRIGGER` (what starts next)

## Quality Rules
- No idle/noise posting.
- No ambiguous RUNNING labels.
- Strategy state and runtime state must stay separate.
- If no meaningful signal, post nothing (`NO_REPLY`).
