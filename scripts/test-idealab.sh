#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/dev-up.sh
./scripts/db-migrate.sh
./scripts/db-seed.sh

PYTHONPATH=. python3 -m unittest tests/test_idealab_unit.py tests/test_idealab_integration.py

echo "test-idealab: SUCCESS"
