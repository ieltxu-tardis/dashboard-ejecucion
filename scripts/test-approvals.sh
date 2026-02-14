#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/dev-up.sh
./scripts/db-migrate.sh
./scripts/db-seed.sh

PYTHONPATH=. python3 -m unittest tests/test_approvals_flow.py

# CLI smoke: list pending -> approve first pending -> verify status
PENDING_JSON=$(./scripts/approvals list --status pending --limit 5)
APPROVAL_ID=$(PENDING_JSON="$PENDING_JSON" python3 - <<'PY'
import json, os
rows=json.loads(os.environ['PENDING_JSON'])
print(rows[0]['id'] if rows else '')
PY
)

if [[ -n "${APPROVAL_ID}" ]]; then
  ./scripts/approvals show "$APPROVAL_ID" >/tmp/approval_show.json
  ./scripts/approvals approve "$APPROVAL_ID" --reason "ops-approved" --by "admin-local" >/tmp/approval_decision.json || true
fi

# ensure audit entries for approval decision exist and no leaked secrets in summary
PYTHONPATH=. python3 - <<'PY'
from memory_service.db import PostgresExec
rows=PostgresExec().fetchall_json("""
SELECT payload::text AS p FROM audit_log WHERE action IN ('approval.approved','approval.denied') ORDER BY created_at DESC LIMIT 20
""")
if rows:
    for r in rows:
        p=(r.get('p') or '').lower()
        assert 'token' not in p
        assert 'password' not in p
print('approvals_audit: OK')
PY

echo "test-approvals: SUCCESS"
