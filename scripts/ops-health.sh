#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHONPATH=. python3 - <<'PY'
from memory_service.db import PostgresExec

db = PostgresExec()

def to_int(v):
    try:
        return int(float(str(v)))
    except Exception:
        return 0

errs = db.fetchone_value("""
SELECT COUNT(*)::text
FROM observability_events
WHERE created_at >= NOW()-INTERVAL '24 hours'
  AND outcome='error'
  AND component IN ('governance','memory')
""")

pending = db.fetchone_value("SELECT COUNT(*)::text FROM approval_requests WHERE status='pending'")
qlag = db.fetchone_value("""
SELECT COALESCE(MAX(EXTRACT(EPOCH FROM (NOW()-scheduled_at))),0)::text
FROM jobs WHERE status='queued'
""")

errs_i = to_int(errs)
pending_i = to_int(pending)
qlag_i = to_int(qlag)

level = 'GREEN'
if errs_i > 25 or qlag_i > 300 or pending_i > 10:
    level = 'YELLOW'
if errs_i > 75 or qlag_i > 900 or pending_i > 30:
    level = 'RED'

print(f'OPS_HEALTH={level}')
print(f'errors_24h={errs_i}')
print(f'pending_approvals={pending_i}')
print(f'queued_lag_s={qlag_i}')
PY
