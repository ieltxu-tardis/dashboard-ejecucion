#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/dev-up.sh
./scripts/db-migrate.sh
./scripts/db-seed.sh

# Stabilize governance tests: clear stale queued backlog that can trigger high-cost backpressure denies.
PYTHONPATH=. python3 - <<'PY'
from memory_service.db import PostgresExec
PostgresExec().execute("UPDATE jobs SET status='canceled', updated_at=NOW() WHERE status='queued';")
print('governance_prep: queue stabilized')
PY

PYTHONPATH=. python3 -m unittest tests/test_governance.py

# Verify audit contains deny + pending approval and no obvious secrets
PYTHONPATH=. python3 - <<'PY'
from memory_service.db import PostgresExec
rows = PostgresExec().fetchall_json("""
SELECT action, target_ref, payload::text AS p
FROM audit_log
WHERE target_type='governance'
ORDER BY created_at DESC
LIMIT 50
""")
assert any(r['target_ref']=='deny' for r in rows), 'missing deny audit'
assert any(r['target_ref']=='pending_approval' for r in rows), 'missing pending approval audit'
for r in rows:
    p=(r.get('p') or '').lower()
    assert 'password' not in p
    assert 'authorization' not in p
print('governance_audit: OK')
PY

echo "test-governance: SUCCESS"
