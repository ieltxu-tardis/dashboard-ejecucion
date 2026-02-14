#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
  echo "[smoke-db] .env not found. Copy .env.example to .env first."
  exit 1
fi

set -a
source ./.env
set +a

if ! docker compose ps >/dev/null 2>&1; then
  echo "[smoke-db] docker compose unavailable"
  exit 1
fi

# Start stack if not already up
if ! docker compose ps --status running postgres | grep -q postgres; then
  echo "[smoke-db] starting compose stack"
  docker compose up -d
fi

./scripts/db-migrate.sh
./scripts/db-seed.sh

required_tables=(
  tenants users documents entities facts events embeddings audit_log job_runs schema_migrations
)
for t in "${required_tables[@]}"; do
  exists=$(docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "SELECT to_regclass('public.${t}') IS NOT NULL;")
  [[ "$exists" == "t" ]] || { echo "[smoke-db] missing table: $t"; exit 1; }
done

echo "[smoke-db] tables check ok"

vector_enabled=$(docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname='vector');")
[[ "$vector_enabled" == "t" ]] || { echo "[smoke-db] vector extension missing"; exit 1; }

echo "[smoke-db] vector extension ok"

# Minimal tenant-scoped insert/read
cat <<'SQL' | docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"
WITH t AS (
  SELECT id FROM tenants WHERE slug='default' LIMIT 1
), d AS (
  INSERT INTO documents(tenant_id, source_type, source_ref, content, content_hash)
  SELECT t.id, 'smoke', 'smoke:test', 'smoke content', encode(digest('smoke content','sha256'),'hex')
  FROM t
  ON CONFLICT (tenant_id, content_hash) DO NOTHING
  RETURNING id, tenant_id
)
SELECT 'ok';
SQL

count_default=$(docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "SELECT COUNT(*) FROM documents d JOIN tenants t ON t.id=d.tenant_id WHERE t.slug='default';")
[[ "$count_default" =~ ^[0-9]+$ ]] || { echo "[smoke-db] count query failed"; exit 1; }

echo "[smoke-db] tenant read/write ok (default docs=${count_default})"
echo "[smoke-db] SUCCESS"
