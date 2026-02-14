# DATA_MODEL.md

## Phase 2 memory-core schema (multi-tenant)

All core tables include `tenant_id` (NOT NULL) except `tenants` and `schema_migrations`.

## Extensions
- `pgcrypto` (UUID / digest helpers)
- `vector` (pgvector)

## Tables

### tenants
- `id UUID PK`
- `slug TEXT UNIQUE NOT NULL`
- `name TEXT NOT NULL`
- `created_at TIMESTAMPTZ`

### users
- `id UUID PK`
- `tenant_id UUID FK -> tenants(id)`
- `handle TEXT`
- `email TEXT`
- `created_at TIMESTAMPTZ`
- Uniques: `(tenant_id, handle)`, `(tenant_id, email)`

### documents
- `id UUID PK`
- `tenant_id UUID FK`
- `source_type TEXT NOT NULL`
- `source_ref TEXT`
- `content TEXT NOT NULL`
- `content_hash TEXT NOT NULL`
- `metadata JSONB`
- `created_at TIMESTAMPTZ`
- Dedupe: `UNIQUE (tenant_id, content_hash)`

### entities
- `id UUID PK`
- `tenant_id UUID FK`
- `type TEXT NOT NULL`
- `name TEXT NOT NULL`
- `attributes JSONB`
- `created_at`, `updated_at`

### facts
- `id UUID PK`
- `tenant_id UUID FK`
- `key TEXT NOT NULL`
- `value JSONB NOT NULL`
- `confidence NUMERIC(4,3)`
- `source_doc_id UUID FK -> documents(id)`
- `created_at`, `updated_at`

### events
- `id UUID PK`
- `tenant_id UUID FK`
- `event_type TEXT NOT NULL`
- `payload JSONB`
- `source_doc_id UUID FK -> documents(id)`
- `created_at`

### embeddings
- `id UUID PK`
- `tenant_id UUID FK`
- `doc_id UUID FK -> documents(id)`
- `chunk_id TEXT NOT NULL`
- `embedding VECTOR(1536) NOT NULL`
- `model TEXT NOT NULL`
- `metadata JSONB`
- `created_at`
- Unique: `(tenant_id, doc_id, chunk_id, model)`

### tasks
- `id UUID PK`
- `tenant_id UUID FK`
- `title TEXT NOT NULL`
- `status TEXT NOT NULL`
- `due_at TIMESTAMPTZ`
- `metadata JSONB`
- `created_at`, `updated_at`

### document_chunks (Phase 4)
- `id UUID PK`
- `tenant_id UUID FK`
- `doc_id UUID FK -> documents(id)`
- `chunk_id TEXT`
- `chunk_text TEXT`
- `chunk_index INT`
- `token_estimate INT`
- `metadata JSONB`
- Unique: `(tenant_id, doc_id, chunk_id)`

### jobs (Phase 4)
- `id UUID PK`
- `tenant_id UUID FK`
- `type TEXT`
- `payload JSONB`
- `status TEXT` (`queued|running|done|failed`)
- `priority INT`
- `dedupe_key TEXT` (unique by tenant)
- `scheduled_at`, `attempts`, `max_attempts`, `timeout_seconds`
- `last_error`, `created_at`, `updated_at`

### audit_log (recommended for next phases)
- `id UUID PK`
- `tenant_id UUID FK`
- `actor_type`, `actor_ref`
- `action`, `target_type`, `target_ref`
- `payload JSONB`
- `created_at`

### job_runs (recommended for queue/worker phases)
- `id UUID PK`
- `tenant_id UUID FK`
- `job_type`, `status`, `attempts`
- `started_at`, `ended_at`
- `error_message`
- `metadata JSONB`

## Indexing strategy (Phase 2)
- Tenant lookup indexes on all core tables.
- Time-ordered indexes for `documents`, `events`, `audit_log`, `job_runs`.
- Functional dedupe via `(tenant_id, content_hash)` on `documents`.

### Vector index note
ANN vector index is intentionally deferred in Phase 2.
Reason: ivfflat/hnsw params depend on live dataset shape; premature config can degrade recall/latency.
This will be introduced in a later phase with measured defaults.

## Seed data
- tenant: `default`
- user: `default-user`

## Verification
- Run `./scripts/smoke-db.sh`
- Confirm tables + extension + tenant-scoped write/read path.
