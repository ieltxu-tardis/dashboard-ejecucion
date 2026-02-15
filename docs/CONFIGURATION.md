# CONFIGURATION.md

## Core env vars

### Governance / Safe mode
- `SAFE_MODE_DISABLE_TOOLS` (0/1)
- `SAFE_MODE_DISABLE_JOB_ENQUEUE` (0/1)
- `SAFE_MODE_DISABLE_FINANCE_WRITE` (0/1)

### Request budgets
- `REQ_MAX_TOOL_CALLS` (default 12)
- `REQ_MAX_JOBS_ENQUEUED` (default 5)
- `REQ_MAX_TOTAL_RUNTIME_MS` (default 120000)

### Backpressure thresholds
- `QUEUE_DEPTH_HIGH` (default 50)
- `QUEUE_LAG_HIGH_SECONDS` (default 120)

### Job worker limits
- `JOB_MAX_RETRY` (default 5)
- `JOB_BACKOFF_BASE_SECONDS` (default 2)
- `JOB_MAX_CHUNKS_PER_DOC` (default 128)
- `JOB_POLL_SECONDS` (default 1.5)

### Metrics
- `METRICS_HOST` (default 127.0.0.1)
- `METRICS_PORT` (default 9464)

### Approvals (Phase 6.1)
- `APPROVAL_TTL_SECONDS` (default 900, i.e. 15m)
- `APPROVALS_ADMIN_ACTOR` (default `admin-local`)

### Capability modules (Phase 7/8/9)
- `MODULES_ENABLED` comma-separated allowlist override (e.g. `idealab,timelab,financelab`)
- default module flags live in `modules/modules.yaml` (fail-closed recommended for new modules)

### FinanceLab (Phase 9)
- `FINANCE_DEFAULT_CURRENCY` (default `USD`)
- `FINANCE_IMPORT_MAX_ROWS` (default `1000`)

### ResearchLab (Phase 10)
- `RESEARCHLAB_DEFAULT_TOP_K` (default `5`)
- `RESEARCHLAB_MAX_NOTE_SIZE` (default `20000` chars)

### DigestHub (Phase 11)
- `DIGESTHUB_DEFAULT_TZ` (default `UTC`)
- `DIGESTHUB_DAILY_HOUR_UTC` (default `9`)
- `DIGESTHUB_WEEKLY_WEEKDAY` (default `1` Monday)
- `DIGESTHUB_WEEKLY_HOUR_UTC` (default `10`)
- `DIGESTHUB_BACKLOG_THRESHOLD` (default `50`, degraded mode trigger)

## Notes
- Keep metrics bound to localhost/internal network.
- Do not expose sensitive service ports publicly.
