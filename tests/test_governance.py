import unittest
from pathlib import Path

from governance.engine import GovernanceEngine, RequestBudget
from governance.tool_runner import ToolRunner
from memory_service.service import PostgresMemoryService, get_default_tenant_id


class GovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = str(Path(__file__).resolve().parents[1])
        cls.runner = ToolRunner(cls.repo)
        svc = PostgresMemoryService.build()
        cls.tenant_id = get_default_tenant_id(svc)

    def test_deny_unregistered_tool(self):
        out = self.runner.run_tool(
            tenant_id=self.tenant_id,
            actor_ref="default-user",
            tool_name="unknown.tool",
            payload={},
            budget=RequestBudget(),
        )
        self.assertEqual(out.status, "deny")
        self.assertEqual(out.reason_code, "tool_not_registered")

    def test_deny_scope(self):
        out = self.runner.run_tool(
            tenant_id=self.tenant_id,
            actor_ref="default-user",
            tool_name="finance.write_transaction",
            payload={},
            budget=RequestBudget(),
        )
        self.assertEqual(out.status, "deny")
        self.assertEqual(out.reason_code, "scope_denied")

    def test_pending_approval(self):
        out = self.runner.run_tool(
            tenant_id=self.tenant_id,
            actor_ref="finance-admin",
            tool_name="finance.write_transaction",
            payload={},
            budget=RequestBudget(),
        )
        self.assertEqual(out.status, "pending_approval")
        self.assertEqual(out.reason_code, "requires_approval")
        self.assertIsNotNone(out.approval_id)

    def test_budget_exhausted(self):
        b = RequestBudget(tool_calls=12)
        out = self.runner.run_tool(
            tenant_id=self.tenant_id,
            actor_ref="default-user",
            tool_name="memory.semantic_search",
            payload={},
            budget=b,
        )
        self.assertEqual(out.status, "deny")
        self.assertEqual(out.reason_code, "budget_tool_calls_exhausted")


if __name__ == "__main__":
    unittest.main()
