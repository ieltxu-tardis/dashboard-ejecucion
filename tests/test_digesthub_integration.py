import unittest
from datetime import datetime, timezone
from pathlib import Path

from memory_service.service import PostgresMemoryService, get_default_tenant_id
from modules.digesthub.service import DigestHubService


class DigestHubIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = str(Path(__file__).resolve().parents[1])
        cls.memory = PostgresMemoryService.build()
        cls.tenant_id = get_default_tenant_id(cls.memory)
        cls.svc = DigestHubService(cls.repo, cls.memory)

    def test_digest_flow(self):
        sub = self.svc.subscribe_daily(
            tenant_id=self.tenant_id,
            actor_ref="digest-it",
            payload={"actor_id": "discord-user-1", "timezone": "UTC", "hour": 9},
        )
        self.assertTrue(sub.get("subscription_id"))

        preview = self.svc.preview_daily(
            tenant_id=self.tenant_id,
            payload={"actor_id": "discord-user-1"},
        )
        self.assertIn("sections", preview)
        self.assertIn("text", preview)

        sent = self.svc.send_now(
            tenant_id=self.tenant_id,
            actor_ref="digest-it",
            payload={"actor_id": "discord-user-1", "period": "daily"},
        )
        self.assertEqual(sent.get("status"), "ok")

        tick = self.svc.tick_due(tenant_id=self.tenant_id, now_utc=datetime(2026, 2, 16, 9, 0, tzinfo=timezone.utc))
        self.assertGreaterEqual(tick.get("checked", 0), 1)

        audits = self.memory.db.fetchall_json(
            """
            SELECT action FROM audit_log
            WHERE tenant_id=%(t)s AND actor_ref='digest-it'
            ORDER BY created_at DESC LIMIT 20
            """,
            params={"t": self.tenant_id},
        )
        self.assertGreaterEqual(len(audits), 2)


if __name__ == "__main__":
    unittest.main()
