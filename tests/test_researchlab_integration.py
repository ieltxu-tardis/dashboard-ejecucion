import time
import unittest
from pathlib import Path

from memory_service.db import PostgresExec
from memory_service.service import PostgresMemoryService, get_default_tenant_id
from modules.researchlab.service import ResearchLabService


class ResearchLabIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = str(Path(__file__).resolve().parents[1])
        cls.memory = PostgresMemoryService.build()
        cls.tenant_id = get_default_tenant_id(cls.memory)
        cls.svc = ResearchLabService(cls.repo, cls.memory)

    def _wait_embeddings(self, doc_id: str, timeout_s: int = 45):
        db = PostgresExec()
        start = time.time()
        while time.time() - start < timeout_s:
            c = int(
                db.fetchone_value(
                    "SELECT COUNT(*)::text FROM embeddings WHERE tenant_id=%(t)s AND doc_id=%(d)s::uuid",
                    params={"t": self.tenant_id, "d": doc_id},
                )
                or "0"
            )
            if c > 0:
                return True
            time.sleep(1)
        return False

    def test_research_flow(self):
        c = self.svc.create_collection(
            tenant_id=self.tenant_id,
            actor_ref="research-it",
            payload={"name": "AI Notes", "description": "model behavior"},
        )
        self.assertTrue(c.get("collection_id"))

        note = self.svc.ingest_note(
            tenant_id=self.tenant_id,
            actor_ref="research-it",
            payload={
                "title": "Embedding behavior",
                "content": "Vector search improves retrieval quality for long docs.",
                "tags": ["retrieval", "embeddings"],
                "collection_id": c["collection_id"],
            },
        )
        self.assertTrue(note.get("doc_id"))
        self.assertTrue(self._wait_embeddings(note["doc_id"]))

        search = self.svc.search(
            tenant_id=self.tenant_id,
            payload={"query_text": "retrieval quality", "top_k": 5},
        )
        self.assertEqual(search.get("status"), "ok")
        self.assertGreaterEqual(len(search.get("hits", [])), 1)
        hit = search["hits"][0]
        self.assertIn("snippet", hit)
        self.assertIn("citation", hit)

        scoped = self.svc.search(
            tenant_id=self.tenant_id,
            payload={"query_text": "retrieval", "collection_id": c["collection_id"], "top_k": 5},
        )
        self.assertEqual(scoped.get("status"), "ok")
        self.assertGreaterEqual(len(scoped.get("hits", [])), 1)

        pack = self.svc.context_pack(
            tenant_id=self.tenant_id,
            payload={"query_text": "why vector search"},
        )
        self.assertEqual(pack.get("status"), "ok")
        self.assertIn("context_pack", pack)

        audits = self.memory.db.fetchall_json(
            """
            SELECT action FROM audit_log
            WHERE tenant_id=%(t)s AND actor_ref='research-it'
            ORDER BY created_at DESC LIMIT 20
            """,
            params={"t": self.tenant_id},
        )
        self.assertGreaterEqual(len(audits), 3)


if __name__ == "__main__":
    unittest.main()
