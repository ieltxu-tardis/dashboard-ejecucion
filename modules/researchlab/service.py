from __future__ import annotations

import hashlib
import os
from typing import Any

from memory_service.embedding_provider import LocalHashEmbeddingProvider
from memory_service.service import PostgresMemoryService
from modules.registry import ModuleRegistry
from observability.logging import log_event

from .schemas import (
    validate_add_to_collection_input,
    validate_create_collection_input,
    validate_ingest_note_input,
    validate_search_input,
)


class ResearchLabService:
    def __init__(self, repo_root: str, memory: PostgresMemoryService):
        self.repo_root = repo_root
        self.memory = memory
        self.modules = ModuleRegistry(repo_root)
        self.embedder = LocalHashEmbeddingProvider()

    def _ensure_enabled(self) -> None:
        if not self.modules.is_enabled("researchlab"):
            raise ValueError("module_disabled:researchlab")

    def _clean_id(self, value: str) -> str:
        return str(value).strip().splitlines()[0]

    def create_collection(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_create_collection_input(payload)
        name = str(payload["name"]).strip().lower()
        desc = payload.get("description")

        existing = self.memory.db.fetchone_value(
            "SELECT id::text FROM research_collections WHERE tenant_id=%(t)s AND lower(name)=%(n)s LIMIT 1",
            params={"t": tenant_id, "n": name},
        )
        if existing:
            cid = self._clean_id(existing)
        else:
            cid = self._clean_id(
                self.memory.db.fetchone_value(
                    """
                    INSERT INTO research_collections(tenant_id, name, description)
                    VALUES (%(t)s, %(n)s, %(d)s)
                    RETURNING id::text;
                    """,
                    params={"t": tenant_id, "n": name, "d": desc},
                )
                or ""
            )
        self.memory.db.execute(
            """
            INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload)
            VALUES (%(t)s, 'user', %(a)s, 'researchlab.create_collection', 'research_collection', %(id)s,
                    jsonb_build_object('name', %(name)s));
            """,
            params={"t": tenant_id, "a": actor_ref, "id": cid, "name": name},
        )
        return {"collection_id": cid, "name": name}

    def list_collections(self, *, tenant_id: str) -> list[dict[str, Any]]:
        self._ensure_enabled()
        return self.memory.db.fetchall_json(
            "SELECT id::text, name, description, created_at, updated_at FROM research_collections WHERE tenant_id=%(t)s ORDER BY created_at DESC LIMIT 100",
            params={"t": tenant_id},
        )

    def add_to_collection(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_add_to_collection_input(payload)
        collection_id = self._clean_id(payload["collection_id"])
        doc_id = self._clean_id(payload["doc_id"])

        self.memory.db.execute(
            """
            INSERT INTO research_collection_documents(tenant_id, collection_id, doc_id)
            VALUES (%(t)s, %(c)s::uuid, %(d)s::uuid)
            ON CONFLICT (tenant_id, collection_id, doc_id) DO NOTHING;
            """,
            params={"t": tenant_id, "c": collection_id, "d": doc_id},
        )
        self.memory.db.execute(
            """
            INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload)
            VALUES (%(t)s, 'user', %(a)s, 'researchlab.add_to_collection', 'research_collection', %(c)s,
                    jsonb_build_object('doc_id', %(d)s));
            """,
            params={"t": tenant_id, "a": actor_ref, "c": collection_id, "d": doc_id},
        )
        return {"ok": True, "collection_id": collection_id, "doc_id": doc_id}

    def ingest_note(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_ingest_note_input(payload)
        max_size = int(os.getenv("RESEARCHLAB_MAX_NOTE_SIZE", "20000"))
        content = str(payload["content"])[:max_size]
        title = str(payload.get("title") or "research_note")
        tags = payload.get("tags", [])
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        out = self.memory.write_document(
            {
                "tenant_id": tenant_id,
                "actor_ref": actor_ref,
                "intent_type": "explicit_command",
                "reason": "research note ingest",
                "source": "researchlab",
                "scope": "research:write",
                "confidence": 0.95,
                "source_type": "research_note",
                "source_ref": title,
                "content": content,
                "content_hash": content_hash,
                "metadata": {"title": title, "tags": tags, "module": "researchlab"},
            }
        )
        doc_id = self._clean_id(out["id"])
        if payload.get("collection_id"):
            self.add_to_collection(
                tenant_id=tenant_id,
                actor_ref=actor_ref,
                payload={"collection_id": payload["collection_id"], "doc_id": doc_id},
            )
        log_event("info", "module.researchlab", "ingest_note", tenant_id=tenant_id)
        return {"doc_id": doc_id, "embedding_job": out.get("embedding_job")}

    def search(self, *, tenant_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_search_input(payload)
        query_text = payload["query_text"]
        top_k = min(int(payload.get("top_k", int(os.getenv("RESEARCHLAB_DEFAULT_TOP_K", "5")))), 20)
        collection_id = payload.get("collection_id")

        qvec = self.embedder.embed_text(query_text)
        hits = self.memory.semantic_search(tenant_id, qvec, top_k=max(top_k * 2, 8))

        allowed_docs: set[str] | None = None
        if collection_id:
            cid = self._clean_id(collection_id)
            rows = self.memory.db.fetchall_json(
                "SELECT doc_id::text FROM research_collection_documents WHERE tenant_id=%(t)s AND collection_id=%(c)s::uuid",
                params={"t": tenant_id, "c": cid},
            )
            allowed_docs = {self._clean_id(r["doc_id"]) for r in rows}

        filtered = []
        for h in hits:
            doc_id = self._clean_id(h["doc_id"])
            if allowed_docs is not None and doc_id not in allowed_docs:
                continue
            citation = {
                "doc_id": doc_id,
                "chunk_id": h.get("chunk_id"),
                "source_type": h.get("source_type"),
                "source_ref": h.get("source_ref"),
            }
            filtered.append(
                {
                    "doc_id": doc_id,
                    "chunk_id": h.get("chunk_id"),
                    "score": float(h.get("distance") or 0.0),
                    "snippet": h.get("snippet"),
                    "citation": citation,
                }
            )
            if len(filtered) >= top_k:
                break

        if not filtered:
            has_docs = int(
                self.memory.db.fetchone_value(
                    "SELECT COUNT(*)::text FROM documents WHERE tenant_id=%(t)s",
                    params={"t": tenant_id},
                )
                or "0"
            )
            if has_docs > 0:
                return {"status": "indexing_or_no_hits", "hits": [], "message": "No indexed chunks matched yet; try again shortly."}

        log_event("info", "module.researchlab", "search", tenant_id=tenant_id, hits=len(filtered))
        return {"status": "ok", "hits": filtered}

    def context_pack(self, *, tenant_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        out = self.search(tenant_id=tenant_id, payload={**payload, "top_k": payload.get("top_k", 8)})
        if out.get("status") != "ok":
            return out
        pack = {
            "query": payload["query_text"],
            "evidence": [
                {
                    "snippet": h["snippet"],
                    "citation": h["citation"],
                    "score": h["score"],
                }
                for h in out["hits"]
            ],
        }
        return {"status": "ok", "context_pack": pack}
