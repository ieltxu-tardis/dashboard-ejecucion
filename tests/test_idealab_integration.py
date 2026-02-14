import unittest
from pathlib import Path

from memory_service.service import PostgresMemoryService, get_default_tenant_id
from modules.idealab.service import IdeaLabService


class IdeaLabIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = str(Path(__file__).resolve().parents[1])
        cls.memory = PostgresMemoryService.build()
        cls.tenant_id = get_default_tenant_id(cls.memory)
        cls.svc = IdeaLabService(cls.repo, cls.memory)

    def test_idealab_flow_and_audit(self):
        idea = self.svc.capture_idea(
            tenant_id=self.tenant_id,
            actor_ref="integration-idealab",
            payload={"title": "MVP onboarding", "summary": "Try a guided onboarding", "tags": ["growth", "activation"]},
        )
        self.assertTrue(idea.get("id"))

        ideas = self.svc.list_ideas(tenant_id=self.tenant_id, payload={"limit": 10})
        self.assertGreaterEqual(len(ideas), 1)

        ev = self.svc.evaluate_idea(
            tenant_id=self.tenant_id,
            actor_ref="integration-idealab",
            payload={"idea_id": idea["id"]},
        )
        self.assertEqual(ev["idea_id"], idea["id"])
        self.assertIn("rubric", ev)

        exp = self.svc.plan_experiment(
            tenant_id=self.tenant_id,
            actor_ref="integration-idealab",
            payload={
                "idea_id": idea["id"],
                "hypothesis": "Guided onboarding improves activation",
                "metric": "activation_rate",
                "plan": "Ship to 20% traffic for 7 days",
            },
        )
        self.assertTrue(exp.get("id"))

        done = self.svc.log_experiment_result(
            tenant_id=self.tenant_id,
            actor_ref="integration-idealab",
            payload={"experiment_id": exp["id"], "result": {"delta": 0.08, "p": 0.04}},
        )
        self.assertTrue(done.get("ok"))

        audits = self.memory.db.fetchall_json(
            """
            SELECT action FROM audit_log
            WHERE tenant_id = %(tenant_id)s
              AND actor_ref = 'integration-idealab'
            ORDER BY created_at DESC
            LIMIT 20
            """,
            params={"tenant_id": self.tenant_id},
        )
        self.assertGreaterEqual(len(audits), 4)


if __name__ == "__main__":
    unittest.main()
