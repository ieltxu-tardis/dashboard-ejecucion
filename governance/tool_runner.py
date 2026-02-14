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

    def run_tool(self, *, tenant_id: str, actor_ref: str, tool_name: str, payload: dict[str, Any], budget: RequestBudget, approval_id: str | None = None) -> ToolRunResult:
        if approval_id:
            ap = self.gov.approvals.show(approval_id)
            if not ap:
                return ToolRunResult(status="deny", reason_code="approval_not_found")
            if ap.get("tenant_id") != tenant_id or ap.get("actor_ref") != actor_ref or ap.get("action") != tool_name:
                return ToolRunResult(status="deny", reason_code="approval_mismatch")
            if ap.get("status") == "approved":
                return ToolRunResult(status="allow", reason_code="approved", output={"ok": True, "tool": tool_name, "approval_id": approval_id})
            if ap.get("status") == "pending":
                return ToolRunResult(status="pending_approval", reason_code="requires_approval", approval_id=approval_id)
            return ToolRunResult(status="deny", reason_code=f"approval_{ap.get('status')}")

        d = self.gov.authorize_tool(tenant_id=tenant_id, actor_ref=actor_ref, tool_name=tool_name, budget=budget, payload=payload)
        if d.status == "deny":
            return ToolRunResult(status="deny", reason_code=d.reason_code)
        if d.status == "pending_approval":
            return ToolRunResult(status="pending_approval", reason_code=d.reason_code, approval_id=d.approval_id)

        # Phase 6 baseline: execution is mocked/contracted; governance enforcement is real.
        return ToolRunResult(status="allow", reason_code="allowed", output={"ok": True, "tool": tool_name})
