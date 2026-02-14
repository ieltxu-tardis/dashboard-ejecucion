#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/dev-up.sh
./scripts/db-migrate.sh
./scripts/db-seed.sh

PYTHONPATH=. python3 -m unittest tests/test_policy.py
PYTHONPATH=. python3 tests/test_memory_integration.py

echo "test-memory: SUCCESS"
