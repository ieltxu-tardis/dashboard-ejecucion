#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/dev-up.sh
./scripts/db-migrate.sh
./scripts/db-seed.sh

# worker for embeddings
PYTHONPATH=. python3 workers/jobs_worker.py >/tmp/researchlab-worker.log 2>&1 &
WPID=$!
cleanup(){ kill "$WPID" >/dev/null 2>&1 || true; }
trap cleanup EXIT
sleep 2

PYTHONPATH=. MODULES_ENABLED=researchlab python3 -m unittest tests/test_researchlab_unit.py tests/test_researchlab_integration.py

echo "test-researchlab: SUCCESS"
