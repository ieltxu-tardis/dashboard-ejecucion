#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/dev-up.sh
./scripts/db-migrate.sh
./scripts/db-seed.sh

PYTHONPATH=. MODULES_ENABLED=digesthub python3 -m unittest tests/test_digesthub_unit.py tests/test_digesthub_integration.py

echo "test-digesthub: SUCCESS"
