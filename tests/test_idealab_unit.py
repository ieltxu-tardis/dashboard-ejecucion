import unittest

from modules.idealab.schemas import (
    IdeaLabSchemaError,
    validate_capture_idea_input,
    validate_evaluate_idea_input,
)
from governance.tool_runner import ToolRunner
from governance.engine import RequestBudget
from memory_service.service import PostgresMemoryService, get_default_tenant_id
from pathlib import Path


class IdeaLabUnitTests(unittest.TestCase):
    def test_schema_validation(self):
        with self.assertRaises(IdeaLabSchemaError):
            validate_capture_idea_input({"title": "x"})
        validate_capture_idea_input({"title": "x", "summary": "ok"})
        with self.assertRaises(IdeaLabSchemaError):
            validate_evaluate_idea_input({})

    def test_policy_gating_scope(self):
        repo = str(Path(__file__).resolve().parents[1])
        runner = ToolRunner(repo)
        svc = PostgresMemoryService.build()
        tenant_id = get_default_tenant_id(svc)

        out = runner.run_tool(
            tenant_id=tenant_id,
            actor_ref="system",
            tool_name="idealab.capture_idea",
            payload={"title": "a", "summary": "b"},
            budget=RequestBudget(),
        )
        self.assertEqual(out.status, "deny")
        self.assertEqual(out.reason_code, "scope_denied")


if __name__ == "__main__":
    unittest.main()
