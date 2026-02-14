from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import GovernanceEngine, RequestBudget


@dataclass
class ToolRunResult:
    status: str
    reason_code: str
    approval_id: str | None = None
    output: dict[str, Any] | None = None


class ToolRunner:
    def __init__(self, repo_root: str):
        self.gov = GovernanceEngine(repo_root)

    def run_tool(self, *, tenant_id: str, actor_ref: str, tool_name: str, payload: dict[str, Any], budget: RequestBudget) -> ToolRunResult:
        d = self.gov.authorize_tool(tenant_id=tenant_id, actor_ref=actor_ref, tool_name=tool_name, budget=budget)
        if d.status == "deny":
            return ToolRunResult(status="deny", reason_code=d.reason_code)
        if d.status == "pending_approval":
            return ToolRunResult(status="pending_approval", reason_code=d.reason_code, approval_id=d.approval_id)

        # Phase 6 baseline: execution is mocked/contracted; governance enforcement is real.
        return ToolRunResult(status="allow", reason_code="allowed", output={"ok": True, "tool": tool_name})
