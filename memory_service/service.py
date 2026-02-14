from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any

from .db import PostgresExec
from .jobs import JobQueueService
from .policy import WritePolicyEngine
from .schemas import validate_document_write, validate_entity_write, validate_fact_write


class IMemoryService(Protocol):
    def write_document(self, payload: dict[str, Any]) -> dict[str, Any]: ...
    def write_entity(self, payload: dict[str, Any]) -> dict[str, Any]: ...
    def write_fact(self, payload: dict[str, Any]) -> dict[str, Any]: ...
    def read_entities(self, tenant_id: str, *, entity_type: str | None = None) -> list[dict[str, Any]]: ...
    def read_facts(self, tenant_id: str, *, key: str | None = None) -> list[dict[str, Any]]: ...
    def read_documents(self, tenant_id: str) -> list[dict[str, Any]]: ...
    def read_events(self, tenant_id: str) -> list[dict[str, Any]]: ...
    def read_tasks(self, tenant_id: str) -> list[dict[str, Any]]: ...
    def semantic_search(self, tenant_id: str, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]: ...


@dataclass
class PostgresMemoryService:
    db: PostgresExec
    policy: WritePolicyEngine
    jobs: JobQueueService | None = None

    @classmethod
    def build(cls) -> "PostgresMemoryService":
        db = PostgresExec()
        return cls(db=db, policy=WritePolicyEngine(), jobs=JobQueueService(db))

    def _policy_gate(self, payload: dict[str, Any], schema_valid: bool) -> None:
        decision = self.policy.evaluate(
            intent_type=payload["intent_type"],
            reason=payload["reason"],
            source=payload["source"],
            scope=payload["scope"],
            confidence=float(payload["confidence"]),
            schema_valid=schema_valid,
        )
        if not decision.allowed:
            raise ValueError(f"write_denied:{decision.reason}")

    def _audit(self, *, tenant_id: str, actor_ref: str, action: str, target_type: str, target_ref: str, source: str, reason: str, confidence: float) -> None:
        self.db.execute(
            """
            INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload)
            VALUES (%(tenant_id)s, 'user', %(actor_ref)s, %(action)s, %(target_type)s, %(target_ref)s,
                    jsonb_build_object('source', %(source)s, 'reason', %(reason)s, 'confidence', %(confidence)s));
            """,
            params={
                "tenant_id": tenant_id,
                "actor_ref": actor_ref,
                "action": action,
                "target_type": target_type,
                "target_ref": target_ref,
                "source": source,
                "reason": reason,
                "confidence": confidence,
            },
        )

    def write_document(self, payload: dict[str, Any]) -> dict[str, Any]:
        validate_document_write(payload)
        self._policy_gate(payload, schema_valid=True)

        doc_id = self.db.fetchone_value(
            """
            WITH ins AS (
              INSERT INTO documents(tenant_id, source_type, source_ref, content, content_hash, metadata)
              VALUES (%(tenant_id)s, %(source_type)s, %(source_ref)s, %(content)s, %(content_hash)s, %(metadata)s::jsonb)
              ON CONFLICT (tenant_id, content_hash)
              DO UPDATE SET metadata = documents.metadata || EXCLUDED.metadata
              RETURNING id::text
            )
            SELECT id FROM ins LIMIT 1;
            """,
            params={
                "tenant_id": payload["tenant_id"],
                "source_type": payload["source_type"],
                "source_ref": payload.get("source_ref", ""),
                "content": payload["content"],
                "content_hash": payload["content_hash"],
                "metadata": payload.get("metadata", {}),
            },
        )
        if not doc_id:
            raise RuntimeError("document_write_failed")

        self._audit(
            tenant_id=payload["tenant_id"],
            actor_ref=payload["actor_ref"],
            action="write_document",
            target_type="document",
            target_ref=doc_id,
            source=payload["source"],
            reason=payload["reason"],
            confidence=float(payload["confidence"]),
        )

        enqueue_result = None
        if self.jobs is not None:
            try:
                enqueue_result = self.jobs.enqueue_embedding_job(tenant_id=payload["tenant_id"], doc_id=doc_id)
            except Exception:
                enqueue_result = {"queued": False, "reason": "enqueue_failed"}

        return {"id": doc_id, "embedding_job": enqueue_result}

    def write_entity(self, payload: dict[str, Any]) -> dict[str, Any]:
        validate_entity_write(payload)
        self._policy_gate(payload, schema_valid=True)
        entity_id = self.db.fetchone_value(
            """
            INSERT INTO entities(tenant_id, type, name, attributes)
            VALUES (%(tenant_id)s, %(entity_type)s, %(name)s, %(attributes)s::jsonb)
            RETURNING id::text;
            """,
            params={
                "tenant_id": payload["tenant_id"],
                "entity_type": payload["entity_type"],
                "name": payload["name"],
                "attributes": payload.get("attributes", {}),
            },
        )
        self._audit(
            tenant_id=payload["tenant_id"],
            actor_ref=payload["actor_ref"],
            action="write_entity",
            target_type="entity",
            target_ref=entity_id or "",
            source=payload["source"],
            reason=payload["reason"],
            confidence=float(payload["confidence"]),
        )
        return {"id": entity_id}

    def write_fact(self, payload: dict[str, Any]) -> dict[str, Any]:
        validate_fact_write(payload)
        self._policy_gate(payload, schema_valid=True)
        fact_id = self.db.fetchone_value(
            """
            INSERT INTO facts(tenant_id, key, value, confidence, source_doc_id)
            VALUES (%(tenant_id)s, %(key)s, %(value)s::jsonb, %(confidence)s, %(source_doc_id)s::uuid)
            RETURNING id::text;
            """,
            params={
                "tenant_id": payload["tenant_id"],
                "key": payload["key"],
                "value": payload["value"],
                "confidence": float(payload["confidence"]),
                "source_doc_id": payload.get("source_doc_id"),
            },
        )
        self._audit(
            tenant_id=payload["tenant_id"],
            actor_ref=payload["actor_ref"],
            action="write_fact",
            target_type="fact",
            target_ref=fact_id or "",
            source=payload["source"],
            reason=payload["reason"],
            confidence=float(payload["confidence"]),
        )
        return {"id": fact_id}

    def read_entities(self, tenant_id: str, *, entity_type: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT id::text, type, name, attributes, created_at, updated_at FROM entities WHERE tenant_id = %(tenant_id)s"
        params = {"tenant_id": tenant_id}
        if entity_type:
            sql += " AND type = %(entity_type)s"
            params["entity_type"] = entity_type
        sql += " ORDER BY created_at DESC LIMIT 100"
        return self.db.fetchall_json(sql, params=params)

    def read_facts(self, tenant_id: str, *, key: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT id::text, key, value, confidence, source_doc_id::text, created_at FROM facts WHERE tenant_id = %(tenant_id)s"
        params = {"tenant_id": tenant_id}
        if key:
            sql += " AND key = %(key)s"
            params["key"] = key
        sql += " ORDER BY created_at DESC LIMIT 100"
        return self.db.fetchall_json(sql, params=params)

    def read_documents(self, tenant_id: str) -> list[dict[str, Any]]:
        return self.db.fetchall_json(
            "SELECT id::text, source_type, source_ref, content_hash, metadata, created_at FROM documents WHERE tenant_id = %(tenant_id)s ORDER BY created_at DESC LIMIT 100",
            params={"tenant_id": tenant_id},
        )

    def read_events(self, tenant_id: str) -> list[dict[str, Any]]:
        return self.db.fetchall_json(
            "SELECT id::text, event_type, payload, source_doc_id::text, created_at FROM events WHERE tenant_id = %(tenant_id)s ORDER BY created_at DESC LIMIT 100",
            params={"tenant_id": tenant_id},
        )

    def read_tasks(self, tenant_id: str) -> list[dict[str, Any]]:
        return self.db.fetchall_json(
            "SELECT id::text, title, status, due_at, metadata, created_at, updated_at FROM tasks WHERE tenant_id = %(tenant_id)s ORDER BY created_at DESC LIMIT 100",
            params={"tenant_id": tenant_id},
        )

    def semantic_search(self, tenant_id: str, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        if not query_embedding:
            return []
        vector = "[" + ",".join(str(float(x)) for x in query_embedding) + "]"
        return self.db.fetchall_json(
            """
            SELECT e.id::text as embedding_id,
                   e.doc_id::text,
                   e.chunk_id,
                   d.source_type,
                   d.source_ref,
                   d.content_hash,
                   left(dc.chunk_text, 220) as snippet,
                   (e.embedding <=> %(vector)s::vector) AS distance,
                   d.metadata,
                   d.created_at
            FROM embeddings e
            JOIN documents d ON d.id = e.doc_id
            LEFT JOIN document_chunks dc
                   ON dc.tenant_id = e.tenant_id
                  AND dc.doc_id = e.doc_id
                  AND dc.chunk_id = e.chunk_id
            WHERE e.tenant_id = %(tenant_id)s
              AND d.tenant_id = %(tenant_id)s
            ORDER BY e.embedding <=> %(vector)s::vector
            LIMIT %(top_k)s
            """,
            params={"tenant_id": tenant_id, "vector": vector, "top_k": int(top_k)},
        )


def get_default_tenant_id(service: PostgresMemoryService) -> str:
    tenant = service.db.fetchone_value(
        "SELECT id::text FROM tenants WHERE slug = 'default' LIMIT 1;"
    )
    if not tenant:
        raise RuntimeError("default_tenant_missing")
    return tenant
