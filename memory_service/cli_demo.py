#!/usr/bin/env python3
from memory_service.service import PostgresMemoryService, get_default_tenant_id


def main() -> None:
    svc = PostgresMemoryService.build()
    tenant_id = get_default_tenant_id(svc)

    doc = svc.write_document(
        {
            "tenant_id": tenant_id,
            "actor_ref": "demo-user",
            "intent_type": "explicit_user_intent",
            "reason": "manual save request",
            "source": "cli_demo",
            "scope": "memory:write",
            "confidence": 0.95,
            "source_type": "manual",
            "source_ref": "demo",
            "content": "Demo document",
            "content_hash": "demo-content-hash-001",
            "metadata": {"demo": True},
        }
    )

    print({"tenant_id": tenant_id, "document_id": doc["id"]})


if __name__ == "__main__":
    main()
