# OBSERVABILITY.md

## Phase 5 baseline

Observability scope in this phase:
- Structured JSON logs (core components)
- Prometheus-compatible `/metrics` endpoint (local only)
- Job and memory activity instrumentation
- Runbook + alert thresholds

## Logging
- Module: `observability/logging.py`
- Output: JSON to stdout
- Redaction: keys containing password/token/secret/key/authorization/cookie/set-cookie
- Large payload truncation enabled

Standard fields:
- timestamp, level, component, message
- request_id, trace_id (if provided)
- tenant_id, user_id (if context exists)
- job_id/job_type/attempt (worker path)
- latency_ms, error_code

## Metrics endpoint
- Server: `observability/metrics_server.py`
- Bind: `127.0.0.1:9464` (localhost only)
- Endpoint: `/metrics`

## Core metrics
- `openclaw_requests_total{component,route,status_class}`
- `openclaw_request_latency_seconds{component,route}`
- `openclaw_errors_total{component,error_code}`
- `openclaw_policy_denied_total{reason}`
- `openclaw_jobs_enqueued_total{job_type}`
- `openclaw_jobs_processed_total{job_type,outcome}`
- `openclaw_job_duration_seconds{job_type}`
- `openclaw_queue_depth`
- `openclaw_job_lag_seconds{job_type}`
- `openclaw_embeddings_generated_total{model}`
- `openclaw_semantic_search_queries_total`
- `openclaw_semantic_search_hits_total`

Label cardinality guardrails:
- No tenant_id/doc_id labels in metrics.

## Optional observability profile
- Compose profile `observability` can be added/extended for Prometheus/Grafana.
- In this phase, metrics server runs standalone (host process).

## Verification
```bash
./scripts/test-observability.sh
```
