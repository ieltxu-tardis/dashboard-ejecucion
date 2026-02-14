# API_MEMORY.md

## Memory Service contract (Phase 3)

Implementation:
- Interface: `IMemoryService`
- Concrete: `PostgresMemoryService`
- Location: `memory_service/`

## Core operations

### Structured reads
- `read_entities(tenant_id, entity_type=None)`
- `read_facts(tenant_id, key=None)`
- `read_documents(tenant_id)`
- `read_events(tenant_id)`
- `read_tasks(tenant_id)`

All reads are tenant-filtered (`tenant_id` required in query path).

### Structured writes (policy-gated)
- `write_document(payload)`
- `write_entity(payload)`
- `write_fact(payload)`

Required fields (all writes):
- `tenant_id`
- `actor_ref`
- `intent_type`
- `reason`
- `source`
- `scope`
- `confidence`

Per-type required fields:
- document: `source_type`, `content`, `content_hash`
- entity: `entity_type`, `name`
- fact: `key`, `value`

### Semantic search
- `semantic_search(tenant_id, query_embedding, top_k=5)`

Notes:
- Uses pgvector distance operator (`<=>`).
- If no embeddings exist yet, returns empty list.
- Embedding generation is deferred to Phase 4 (queue/workers).

### Audit
Each successful write records an `audit_log` row:
- tenant_id
- actor_ref
- action
- target_type/target_ref
- payload subset (`source`, `reason`, `confidence`)

## Error model (current)
- `write_denied:<reason>` for policy blocks
- `missing_fields:<...>` for schema validation
- runtime DB errors bubble with concise message

## Usage example (Python)

```python
from memory_service.service import PostgresMemoryService, get_default_tenant_id

svc = PostgresMemoryService.build()
tenant_id = get_default_tenant_id(svc)

doc = svc.write_document({
  "tenant_id": tenant_id,
  "actor_ref": "user-1",
  "intent_type": "explicit_user_intent",
  "reason": "user asked to store",
  "source": "chat",
  "scope": "memory:write",
  "confidence": 0.95,
  "source_type": "manual",
  "content": "remember this",
  "content_hash": "abc123",
})
```

## Verification

```bash
./scripts/test-memory.sh
```
