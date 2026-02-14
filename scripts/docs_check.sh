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
  *)
    fail "usage: ./docs_check <0|1>"
    ;;
esac
