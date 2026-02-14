# ADR 0001: PostgreSQL + pgvector as memory foundation

- Status: Accepted (Phase 0)
- Date: 2026-02-14

## Context
The system needs a durable memory foundation that supports:
- structured/auditable data,
- semantic retrieval,
- multi-tenant isolation,
- single-VPS OSS deployment,
- future scalability without immediate infra sprawl.

Current state uses file-memory and lacks a stable data/observability plane.

## Decision
Adopt PostgreSQL as system-of-record and pgvector in the same Postgres instance for semantic embeddings.

## Decision drivers
- OSS, mature, self-hosted friendly.
- Single operational surface for backups and access controls.
- SQL + JSONB flexibility for evolving schemas.
- pgvector avoids introducing a second datastore too early.

## Considered options
1. Postgres + pgvector (**chosen**)
2. Postgres + external vector DB now (deferred)
3. External managed memory stack (rejected: cost/control mismatch)

## Consequences
### Positive
- Lower operational complexity early.
- Strong transactional guarantees for structured memory.
- Straight path to tenant-scoped indexing and auditability.

### Negative / trade-offs
- Vector-heavy workloads may outgrow pgvector tuning limits.
- Requires careful migration/version discipline.

## Migration/exit strategy
- Define vector access behind Memory Service interface.
- Keep vector operations adapterized.
- If scale requires, move semantic index to dedicated vector DB later without changing upstream contracts.

## Structured contract stub (v0)

```yaml
memory_backend_contract_v0:
  truth_store: postgres
  vector_store: pgvector
  tenant_scope: required
  interfaces:
    - write_memory
    - read_memory_structured
    - semantic_search
    - episodic_summaries
    - audit_log
  guarantees:
    - source_attribution_required
    - confidence_field_required
    - audit_event_on_write
```

## Verification checklist
- [ ] Postgres + pgvector service starts via compose
- [ ] migration framework creates tenant-scoped core tables
- [ ] semantic query returns tenant-filtered results
- [ ] write path records source + confidence + audit ref
