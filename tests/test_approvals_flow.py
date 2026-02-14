import unittest
from pathlib import Path

from governance.tool_runner import ToolRunner
from governance.engine import RequestBudget
from memory_service.service import PostgresMemoryService, get_default_tenant_id


class ApprovalsFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = str(Path(__file__).resolve().parents[1])
        cls.runner = ToolRunner(cls.repo)
        svc = PostgresMemoryService.build()
        cls.tenant_id = get_default_tenant_id(svc)

    def test_pending_then_approve_then_resume(self):
        b = RequestBudget()
        out = self.runner.run_tool(
            tenant_id=self.tenant_id,
            actor_ref="finance-admin",
            tool_name="finance.write_transaction",
            payload={"amount": 100, "token": "secret-should-not-appear"},
            budget=b,
        )
        self.assertEqual(out.status, "pending_approval")
        self.assertTrue(out.approval_id)

        dec = self.runner.gov.approvals.decide(
            approval_id=out.approval_id,
            decision="approved",
            decided_by="admin-local",
            reason="validated manually",
        )
        self.assertEqual(dec["status"], "ok")

        resumed = self.runner.run_tool(
            tenant_id=self.tenant_id,
            actor_ref="finance-admin",
            tool_name="finance.write_transaction",
            payload={"amount": 100},
            budget=RequestBudget(),
            approval_id=out.approval_id,
        )
        self.assertEqual(resumed.status, "allow")


if __name__ == "__main__":
    unittest.main()
