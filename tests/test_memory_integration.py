#!/usr/bin/env python3
from memory_service.service import PostgresMemoryService, get_default_tenant_id


def main() -> None:
    svc = PostgresMemoryService.build()
    tenant_id = get_default_tenant_id(svc)

    doc = svc.write_document(
        {
            "tenant_id": tenant_id,
            "actor_ref": "integration-test",
            "intent_type": "explicit_user_intent",
            "reason": "test document",
            "source": "integration",
            "scope": "memory:write",
            "confidence": 0.95,
            "source_type": "integration",
            "source_ref": "itest-1",
            "content": "integration-doc-content",
            "content_hash": "itest-content-hash-001",
            "metadata": {"test": True},
        }
    )

    _entity = svc.write_entity(
        {
            "tenant_id": tenant_id,
            "actor_ref": "integration-test",
            "intent_type": "explicit_command",
            "reason": "test entity",
            "source": "integration",
            "scope": "memory:write",
            "confidence": 0.92,
            "entity_type": "project",
            "name": "Integration Project",
            "attributes": {"stage": "phase3"},
        }
    )

    _fact = svc.write_fact(
        {
            "tenant_id": tenant_id,
            "actor_ref": "integration-test",
            "intent_type": "explicit_command",
            "reason": "test fact",
            "source": "integration",
            "scope": "memory:write",
            "confidence": 0.93,
            "key": "phase",
            "value": {"name": "phase3"},
            "source_doc_id": doc["id"],
        }
    )

    docs = svc.read_documents(tenant_id)
    entities = svc.read_entities(tenant_id)
    facts = svc.read_facts(tenant_id, key="phase")

    assert len(docs) >= 1
    assert len(entities) >= 1
    assert len(facts) >= 1

    audits = svc.db.fetchall_json(
        "SELECT id::text, action FROM audit_log WHERE tenant_id = %(tenant_id)s ORDER BY created_at DESC LIMIT 10",
        params={"tenant_id": tenant_id},
    )
    assert len(audits) >= 3

    print("integration_memory: OK")


if __name__ == "__main__":
    main()
