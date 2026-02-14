#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
  echo "[db-migrate] .env not found. Copy .env.example to .env first."
  exit 1
fi

set -a
source ./.env
set +a

if ! docker compose ps postgres >/dev/null 2>&1; then
  echo "[db-migrate] docker compose not available for postgres service."
  exit 1
fi

# Wait for postgres readiness
for i in $(seq 1 30); do
  if docker compose exec -T postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

# Ensure schema_migrations exists
cat migrations/0000_schema_migrations.sql | docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"

for f in migrations/[0-9][0-9][0-9][0-9]_*.sql; do
  version="$(basename "$f")"
  already=$(docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "SELECT 1 FROM schema_migrations WHERE version='${version}' LIMIT 1;")
  if [[ "$already" == "1" ]]; then
    echo "[db-migrate] skip $version"
    continue
  fi

  echo "[db-migrate] apply $version"
  cat "$f" | docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"
  docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "INSERT INTO schema_migrations(version) VALUES ('${version}');"
done

echo "[db-migrate] done"
