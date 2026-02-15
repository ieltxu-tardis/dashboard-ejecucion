# ADR 0005 - Digest scheduler strategy

## Context
DigestHub needs periodic daily/weekly sends with minimal operational overhead.

## Decision
Use **option 2**: lightweight CLI tick (`scripts/digest-tick.sh`) suitable for cron/systemd.

## Rationale
- No always-on scheduler process required for MVP.
- Keeps architecture simple and auditable.
- Works with existing deployment patterns.

## Consequences
- Operator must configure cron/systemd explicitly.
- Tick cadence controls send precision (recommended: every 60 minutes).
