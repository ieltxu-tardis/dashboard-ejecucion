#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
  echo "[db-seed] .env not found. Copy .env.example to .env first."
  exit 1
fi

set -a
source ./.env
set +a

cat migrations/0004_seed_default.sql | docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"
echo "[db-seed] done"
