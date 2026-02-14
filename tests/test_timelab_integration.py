import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone

from memory_service.service import PostgresMemoryService, get_default_tenant_id
from modules.timelab.service import TimeLabService


class TimeLabIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = str(Path(__file__).resolve().parents[1])
        cls.memory = PostgresMemoryService.build()
        cls.tenant_id = get_default_tenant_id(cls.memory)
        cls.svc = TimeLabService(cls.repo, cls.memory)

    def test_timelab_flow(self):
        due = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        t1 = self.svc.capture_task(
            tenant_id=self.tenant_id,
            actor_ref="timelab-it",
            payload={"title": "Prepare weekly plan", "tags": ["planning"], "priority": "high", "due_at": due},
        )
        t2 = self.svc.capture_task(
            tenant_id=self.tenant_id,
            actor_ref="timelab-it",
            payload={"title": "Inbox zero", "tags": ["ops"], "priority": "normal"},
        )
        self.assertTrue(t1.get("id"))
        self.assertTrue(t2.get("id"))

        open_tasks = self.svc.list_tasks(tenant_id=self.tenant_id, payload={"status": "open"})
        self.assertGreaterEqual(len(open_tasks), 2)

        ranged = self.svc.list_tasks(tenant_id=self.tenant_id, payload={"due_from": datetime.now(timezone.utc).isoformat(), "due_to": (datetime.now(timezone.utc)+timedelta(days=5)).isoformat()})
        self.assertGreaterEqual(len(ranged), 1)

        upd = self.svc.update_task(
            tenant_id=self.tenant_id,
            actor_ref="timelab-it",
            payload={"task_id": t1["id"], "status": "done"},
        )
        self.assertTrue(upd.get("updated"))

        g = self.svc.capture_goal(
            tenant_id=self.tenant_id,
            actor_ref="timelab-it",
            payload={"title": "Ship TimeLab MVP", "notes": "before next phase", "tags": ["roadmap"]},
        )
        self.assertTrue(g.get("id"))

        goals = self.svc.list_goals(tenant_id=self.tenant_id)
        self.assertGreaterEqual(len(goals), 1)

        preview = self.svc.weekly_review(
            tenant_id=self.tenant_id,
            actor_ref="timelab-it",
            payload={"persist": False},
        )
        self.assertFalse(preview["persisted"])
        self.assertIn("summary", preview)

        persisted = self.svc.weekly_review(
            tenant_id=self.tenant_id,
            actor_ref="timelab-it",
            payload={"persist": True},
        )
        self.assertTrue(persisted["persisted"])
        self.assertTrue(persisted.get("document_id"))

        audits = self.memory.db.fetchall_json(
            """
            SELECT action FROM audit_log
            WHERE tenant_id = %(tenant_id)s
              AND actor_ref = 'timelab-it'
            ORDER BY created_at DESC
            LIMIT 30
            """,
            params={"tenant_id": self.tenant_id},
        )
        self.assertGreaterEqual(len(audits), 5)


if __name__ == "__main__":
    unittest.main()
