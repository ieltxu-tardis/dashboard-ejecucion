#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
PHASE="${1:-}"

fail() {
  echo "docs_check: FAIL - $1"
  exit 1
}

pass() {
  echo "docs_check: OK - $1"
}

case "$PHASE" in
  0)
    [[ -f docs/ARCHITECTURE.md ]] || fail "missing docs/ARCHITECTURE.md"
    [[ -f docs/ROADMAP.md ]] || fail "missing docs/ROADMAP.md"
    [[ -f docs/adr/0001-postgres-pgvector.md ]] || fail "missing docs/adr/0001-postgres-pgvector.md"
    pass "phase 0 docs present"
    ;;
  1)
    [[ -f docker-compose.yml ]] || fail "missing docker-compose.yml"
    [[ -f .env.example ]] || fail "missing .env.example"
    [[ -f scripts/dev-up.sh ]] || fail "missing scripts/dev-up.sh"
    [[ -f scripts/dev-down.sh ]] || fail "missing scripts/dev-down.sh"
    [[ -f docs/DEPLOY_VPS.md ]] || fail "missing docs/DEPLOY_VPS.md"
    pass "phase 1 infra/docs artifacts present"
    ;;
  2)
    [[ -f migrations/0000_schema_migrations.sql ]] || fail "missing migrations/0000_schema_migrations.sql"
    [[ -f migrations/0001_extensions.sql ]] || fail "missing migrations/0001_extensions.sql"
    [[ -f migrations/0002_core_schema.sql ]] || fail "missing migrations/0002_core_schema.sql"
    [[ -f migrations/0003_indexes.sql ]] || fail "missing migrations/0003_indexes.sql"
    [[ -f migrations/0004_seed_default.sql ]] || fail "missing migrations/0004_seed_default.sql"
    [[ -f migrations/0005_tasks.sql ]] || fail "missing migrations/0005_tasks.sql"
    [[ -f scripts/db-migrate.sh ]] || fail "missing scripts/db-migrate.sh"
    [[ -f scripts/db-seed.sh ]] || fail "missing scripts/db-seed.sh"
    [[ -f scripts/smoke-db.sh ]] || fail "missing scripts/smoke-db.sh"
    [[ -f docs/DATA_MODEL.md ]] || fail "missing docs/DATA_MODEL.md"
    [[ -f docs/DB_MIGRATIONS.md ]] || fail "missing docs/DB_MIGRATIONS.md"
    pass "phase 2 db migration/schema artifacts present"
    ;;
  3)
    [[ -f docs/API_MEMORY.md ]] || fail "missing docs/API_MEMORY.md"
    [[ -f docs/POLICY.md ]] || fail "missing docs/POLICY.md"
    [[ -f memory_service/service.py ]] || fail "missing memory_service/service.py"
    [[ -f memory_service/policy.py ]] || fail "missing memory_service/policy.py"
    [[ -f scripts/test-memory.sh ]] || fail "missing scripts/test-memory.sh"
    pass "phase 3 memory service/policy/docs artifacts present"
    ;;
  *)
    fail "usage: ./docs_check <0|1|2|3>"
    ;;
esac
