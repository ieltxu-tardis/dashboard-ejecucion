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
  4)
    [[ -f docs/JOBS_QUEUE.md ]] || fail "missing docs/JOBS_QUEUE.md"
    [[ -f docs/EMBEDDINGS.md ]] || fail "missing docs/EMBEDDINGS.md"
    [[ -f docs/adr/0004-queue-workers.md ]] || fail "missing docs/adr/0004-queue-workers.md"
    [[ -f migrations/0006_jobs.sql ]] || fail "missing migrations/0006_jobs.sql"
    [[ -f migrations/0007_document_chunks.sql ]] || fail "missing migrations/0007_document_chunks.sql"
    [[ -f workers/jobs_worker.py ]] || fail "missing workers/jobs_worker.py"
    [[ -f workers/enqueue_job.py ]] || fail "missing workers/enqueue_job.py"
    [[ -f scripts/test-jobs.sh ]] || fail "missing scripts/test-jobs.sh"
    pass "phase 4 queue/worker/docs artifacts present"
    ;;
  5)
    [[ -f docs/OBSERVABILITY.md ]] || fail "missing docs/OBSERVABILITY.md"
    [[ -f docs/ALERTS.md ]] || fail "missing docs/ALERTS.md"
    [[ -f docs/RUNBOOK.md ]] || fail "missing docs/RUNBOOK.md"
    [[ -f observability/logging.py ]] || fail "missing observability/logging.py"
    [[ -f observability/metrics_server.py ]] || fail "missing observability/metrics_server.py"
    [[ -f migrations/0008_observability.sql ]] || fail "missing migrations/0008_observability.sql"
    [[ -f scripts/test-observability.sh ]] || fail "missing scripts/test-observability.sh"
    pass "phase 5 observability artifacts present"
    ;;
  6)
    [[ -f governance/tool_registry.yaml ]] || fail "missing governance/tool_registry.yaml"
    [[ -f governance/scopes.yaml ]] || fail "missing governance/scopes.yaml"
    [[ -f governance/engine.py ]] || fail "missing governance/engine.py"
    [[ -f governance/tool_runner.py ]] || fail "missing governance/tool_runner.py"
    [[ -f governance/rate_limit.py ]] || fail "missing governance/rate_limit.py"
    [[ -f docs/SECURITY.md ]] || fail "missing docs/SECURITY.md"
    [[ -f docs/CONFIGURATION.md ]] || fail "missing docs/CONFIGURATION.md"
    [[ -f scripts/test-governance.sh ]] || fail "missing scripts/test-governance.sh"
    [[ -f migrations/0009_governance.sql ]] || fail "missing migrations/0009_governance.sql"
    pass "phase 6 governance artifacts present"
    ;;
  *)
    fail "usage: ./docs_check <0|1|2|3|4|5|6>"
    ;;
esac
