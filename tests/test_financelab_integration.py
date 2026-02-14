import hashlib
import unittest
from pathlib import Path

from memory_service.service import PostgresMemoryService, get_default_tenant_id
from modules.financelab.service import FinanceLabService


class FinanceLabIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = str(Path(__file__).resolve().parents[1])
        cls.memory = PostgresMemoryService.build()
        cls.tenant_id = get_default_tenant_id(cls.memory)
        cls.svc = FinanceLabService(cls.repo, cls.memory)
        csv_path = Path(cls.repo) / "tests/fixtures/finance_sample.csv"
        content = csv_path.read_text()
        ch = hashlib.sha256(content.encode("utf-8")).hexdigest()
        cls.doc = cls.memory.write_document(
            {
                "tenant_id": cls.tenant_id,
                "actor_ref": "fin-test",
                "intent_type": "explicit_command",
                "reason": "finance import source",
                "source": "financelab-test",
                "scope": "memory:write",
                "confidence": 0.95,
                "source_type": "csv",
                "source_ref": "fixture-finance",
                "content": content,
                "content_hash": ch,
                "metadata": {"kind": "finance_csv"},
            }
        )

    def test_preview_and_commit_with_approval(self):
        preview = self.svc.import_preview_csv(
            tenant_id=self.tenant_id,
            actor_ref="finance-admin",
            payload={
                "source_doc_id": self.doc["id"],
                "mapping": {"date": "date", "amount": "amount", "merchant": "merchant", "category": "category", "note": "note"},
                "currency": "USD",
            },
        )
        self.assertTrue(preview.get("import_id"))
        self.assertEqual(preview["summary"]["count"], 3)

        first = self.svc.commit_import(
            tenant_id=self.tenant_id,
            actor_ref="finance-admin",
            payload={"import_id": preview["import_id"]},
        )
        self.assertEqual(first["status"], "pending_approval")
        approval_id = first["approval_id"]
        self.assertTrue(approval_id)

        dec = self.svc.runner.gov.approvals.decide(
            approval_id=approval_id,
            decision="approved",
            decided_by="admin-local",
            reason="ok",
        )
        self.assertEqual(dec["status"], "ok")

        second = self.svc.commit_import(
            tenant_id=self.tenant_id,
            actor_ref="finance-admin",
            payload={"import_id": preview["import_id"], "approval_id": approval_id},
        )
        self.assertEqual(second["status"], "ok")
        self.assertEqual(second["inserted"] + second["deduped"], 3)

        third = self.svc.commit_import(
            tenant_id=self.tenant_id,
            actor_ref="finance-admin",
            payload={"import_id": preview["import_id"], "approval_id": approval_id},
        )
        self.assertEqual(third["status"], "ok")

        summary = self.svc.spend_summary(tenant_id=self.tenant_id, payload={"group_by": "category"})
        self.assertGreater(summary["total"], 0)

        tx_count = int(self.memory.db.fetchone_value("SELECT COUNT(*)::text FROM finance_transactions WHERE tenant_id=%(t)s", params={"t": self.tenant_id}) or "0")
        self.assertGreaterEqual(tx_count, 3)


if __name__ == "__main__":
    unittest.main()
