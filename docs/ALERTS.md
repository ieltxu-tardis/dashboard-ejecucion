# ALERTS.md

## Initial thresholds (Phase 5)

These are conservative defaults; tune with real traffic.

- Error rate high:
  - Trigger: `openclaw_errors_total / openclaw_requests_total > 0.05` over 10m
- Request latency high:
  - Trigger: `openclaw_request_latency_seconds > 2.5` avg over 10m
- Queue buildup:
  - Trigger: `openclaw_queue_depth > 50` for 5m
- Job lag rising:
  - Trigger: `openclaw_job_lag_seconds > 120` for 5m
- Embedding failures spike:
  - Trigger: worker `job_process` errors for `embed_document` > 5 in 10m

## Operational response levels
- P1: latency/error spike with user impact
- P2: queue growth without user-visible impact yet
- P3: low-volume transient failures

## Notes
- Keep labels low-cardinality.
- Avoid tenant-specific metrics labels; investigate tenant issues via logs + SQL.
