#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/dev-up.sh
./scripts/db-migrate.sh
./scripts/db-seed.sh

PYTHONPATH=. MODULES_ENABLED=timelab python3 -m unittest tests/test_timelab_unit.py tests/test_timelab_integration.py

echo "test-timelab: SUCCESS"
