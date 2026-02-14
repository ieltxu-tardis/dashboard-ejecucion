#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/dev-up.sh
./scripts/db-migrate.sh
./scripts/db-seed.sh

PYTHONPATH=. MODULES_ENABLED=financelab python3 -m unittest tests/test_financelab_unit.py tests/test_financelab_integration.py

# Verify finance writes + approvals audit without obvious secrets
PYTHONPATH=. python3 - <<'PY'
from memory_service.db import PostgresExec
rows = PostgresExec().fetchall_json("""
SELECT action, payload::text p
FROM audit_log
WHERE action LIKE 'financelab.%' OR action LIKE 'approval.%'
ORDER BY created_at DESC
LIMIT 40
""")
assert rows, 'missing finance/approval audit rows'
for r in rows:
    p=(r.get('p') or '').lower()
    assert 'csv' not in p
    assert 'coffee hub' not in p
print('financelab_audit: OK')
PY

echo "test-financelab: SUCCESS"
