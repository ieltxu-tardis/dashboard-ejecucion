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

## Notes
- Keep metrics bound to localhost/internal network.
- Do not expose sensitive service ports publicly.
