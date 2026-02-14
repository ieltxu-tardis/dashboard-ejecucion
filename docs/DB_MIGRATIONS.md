# DB_MIGRATIONS.md

## Migration runner

This repo uses a minimal SQL migration runner:
- migration files in `migrations/`
- migration ledger table: `schema_migrations`
- script: `./scripts/db-migrate.sh`

## Files
- `0000_schema_migrations.sql` (bootstrap ledger)
- `0001_extensions.sql`
- `0002_core_schema.sql`
- `0003_indexes.sql`
- `0004_seed_default.sql` (seed path, also runnable via `db-seed.sh`)

## How to run

```bash
cp .env.example .env
# edit .env with real password
./scripts/dev-up.sh
./scripts/db-migrate.sh
./scripts/db-seed.sh
```

## Rollback strategy (Phase 2)
Current rollback mode is **snapshot restore**:
1. stop writers
2. restore PostgreSQL volume backup
3. rerun smoke checks

Down-migrations are intentionally not added yet to reduce accidental destructive rollbacks during foundation stage.

## Troubleshooting

### `.env not found`
Create `.env` from `.env.example`.

### migration already applied
Runner checks `schema_migrations` and skips existing versions.

### extension errors
Ensure image is `pgvector/pgvector:pg16` and container is healthy.

### psql auth errors
Verify `POSTGRES_USER`, `POSTGRES_DB`, `POSTGRES_PASSWORD` in `.env`.

## Verification

```bash
./scripts/smoke-db.sh
```
Expected: SUCCESS + table checks + vector extension enabled.
