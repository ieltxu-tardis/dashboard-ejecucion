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
    [[ -f scripts/test-approvals.sh ]] || fail "missing scripts/test-approvals.sh"
    [[ -f scripts/approvals ]] || fail "missing scripts/approvals"
    [[ -f governance/approvals.py ]] || fail "missing governance/approvals.py"
    [[ -f governance/approvals_cli.py ]] || fail "missing governance/approvals_cli.py"
    [[ -f migrations/0009_governance.sql ]] || fail "missing migrations/0009_governance.sql"
    [[ -f migrations/0010_approvals_flow.sql ]] || fail "missing migrations/0010_approvals_flow.sql"
    pass "phase 6 governance+approvals artifacts present"
    ;;
  7)
    [[ -f modules/registry.py ]] || fail "missing modules/registry.py"
    [[ -f modules/modules.yaml ]] || fail "missing modules/modules.yaml"
    [[ -f modules/idealab/schemas.py ]] || fail "missing modules/idealab/schemas.py"
    [[ -f modules/idealab/tools.py ]] || fail "missing modules/idealab/tools.py"
    [[ -f modules/idealab/service.py ]] || fail "missing modules/idealab/service.py"
    [[ -f modules/idealab/docs/MODULE_idealab.md ]] || fail "missing modules/idealab/docs/MODULE_idealab.md"
    [[ -f docs/IDEALAB.md ]] || fail "missing docs/IDEALAB.md"
    [[ -f scripts/test-idealab.sh ]] || fail "missing scripts/test-idealab.sh"
    pass "phase 7 capability module artifacts present"
    ;;
  8)
    [[ -f modules/timelab/schemas.py ]] || fail "missing modules/timelab/schemas.py"
    [[ -f modules/timelab/tools.py ]] || fail "missing modules/timelab/tools.py"
    [[ -f modules/timelab/service.py ]] || fail "missing modules/timelab/service.py"
    [[ -f modules/timelab/docs/MODULE_timelab.md ]] || fail "missing modules/timelab/docs/MODULE_timelab.md"
    [[ -f docs/TIMELAB.md ]] || fail "missing docs/TIMELAB.md"
    [[ -f scripts/test-timelab.sh ]] || fail "missing scripts/test-timelab.sh"
    [[ -f docs/POLICY.md ]] || fail "missing docs/POLICY.md"
    pass "phase 8 timelab artifacts present"
    ;;
  9)
    [[ -f migrations/0011_finance.sql ]] || fail "missing migrations/0011_finance.sql"
    [[ -f modules/financelab/schemas.py ]] || fail "missing modules/financelab/schemas.py"
    [[ -f modules/financelab/tools.py ]] || fail "missing modules/financelab/tools.py"
    [[ -f modules/financelab/service.py ]] || fail "missing modules/financelab/service.py"
    [[ -f modules/financelab/docs/MODULE_financelab.md ]] || fail "missing modules/financelab/docs/MODULE_financelab.md"
    [[ -f docs/FINANCELAB.md ]] || fail "missing docs/FINANCELAB.md"
    [[ -f scripts/test-financelab.sh ]] || fail "missing scripts/test-financelab.sh"
    [[ -f docs/POLICY.md ]] || fail "missing docs/POLICY.md"
    pass "phase 9 financelab artifacts present"
    ;;
  10)
    [[ -f migrations/0012_researchlab.sql ]] || fail "missing migrations/0012_researchlab.sql"
    [[ -f modules/researchlab/schemas.py ]] || fail "missing modules/researchlab/schemas.py"
    [[ -f modules/researchlab/tools.py ]] || fail "missing modules/researchlab/tools.py"
    [[ -f modules/researchlab/service.py ]] || fail "missing modules/researchlab/service.py"
    [[ -f modules/researchlab/docs/MODULE_researchlab.md ]] || fail "missing modules/researchlab/docs/MODULE_researchlab.md"
    [[ -f docs/RESEARCHLAB.md ]] || fail "missing docs/RESEARCHLAB.md"
    [[ -f scripts/test-researchlab.sh ]] || fail "missing scripts/test-researchlab.sh"
    [[ -f docs/POLICY.md ]] || fail "missing docs/POLICY.md"
    pass "phase 10 researchlab artifacts present"
    ;;
  11)
    [[ -f migrations/0013_digesthub.sql ]] || fail "missing migrations/0013_digesthub.sql"
    [[ -f modules/digesthub/schemas.py ]] || fail "missing modules/digesthub/schemas.py"
    [[ -f modules/digesthub/tools.py ]] || fail "missing modules/digesthub/tools.py"
    [[ -f modules/digesthub/service.py ]] || fail "missing modules/digesthub/service.py"
    [[ -f modules/digesthub/docs/MODULE_digesthub.md ]] || fail "missing modules/digesthub/docs/MODULE_digesthub.md"
    [[ -f docs/DIGESTHUB.md ]] || fail "missing docs/DIGESTHUB.md"
    [[ -f scripts/test-digesthub.sh ]] || fail "missing scripts/test-digesthub.sh"
    [[ -f docs/POLICY.md ]] || fail "missing docs/POLICY.md"
    pass "phase 11 digesthub artifacts present"
    ;;
  *)
    fail "usage: ./docs_check <0|1|2|3|4|5|6|7|8|9|10|11>"
    ;;
esac
