from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import yaml

from memory_service.db import PostgresExec
from .config import load_config
from .rate_limit import RedisRateLimiter


@dataclass
class Decision:
    status: str  # allow | deny | pending_approval
    reason_code: str
    approval_id: str | None = None


@dataclass
class RequestBudget:
    tool_calls: int = 0
    jobs_enqueued: int = 0
    total_runtime_ms: int = 0


class GovernanceEngine:
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.db = PostgresExec(repo_root=repo_root)
        self.cfg = load_config()
        self.registry = yaml.safe_load((Path(repo_root) / "governance/tool_registry.yaml").read_text())
        self.scopes = yaml.safe_load((Path(repo_root) / "governance/scopes.yaml").read_text())
        self.ratelimiter = RedisRateLimiter(repo_root)

    def _audit(self, tenant_id: str, actor_ref: str, action: str, outcome: str, reason: str, payload: dict | None = None):
        self.db.execute(
            """
            INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload)
            VALUES (%(tenant_id)s, 'actor', %(actor_ref)s, %(action)s, 'governance', %(outcome)s,
                    jsonb_build_object('reason_code', %(reason)s, 'meta', %(payload)s::jsonb));
            """,
            params={
                "tenant_id": tenant_id,
                "actor_ref": actor_ref,
                "action": action,
                "outcome": outcome,
                "reason": reason,
                "payload": payload or {},
            },
        )
        self.db.execute(
            """
            INSERT INTO observability_events(tenant_id, component, route, event_type, outcome, error_code, payload)
            VALUES (%(tenant_id)s, 'governance', %(route)s,
                    CASE WHEN %(outcome)s='allow' THEN 'policy_allowed' ELSE 'policy_denied' END,
                    CASE WHEN %(outcome)s='allow' THEN '2xx' ELSE 'error' END,
                    %(reason)s, '{}'::jsonb);
            """,
            params={"tenant_id": tenant_id, "route": action, "outcome": outcome, "reason": reason},
        )

    def _get_tool(self, tool_name: str) -> dict | None:
        for t in self.registry.get("tools", []):
            if t.get("name") == tool_name:
                return t
        return None

    def _actor_scopes(self, actor_ref: str) -> set[str]:
        return set(self.scopes.get("actors", {}).get(actor_ref, []))

    def _backpressure_high(self) -> bool:
        qd = int(self.db.fetchone_value("SELECT COUNT(*)::text FROM jobs WHERE status='queued'") or "0")
        lag = float(self.db.fetchone_value("SELECT COALESCE(MAX(EXTRACT(EPOCH FROM (NOW()-scheduled_at))),0)::text FROM jobs WHERE status='queued'") or "0")
        return qd >= self.cfg.queue_depth_high or lag >= self.cfg.queue_lag_high_seconds

    def authorize_tool(self, *, tenant_id: str, actor_ref: str, tool_name: str, budget: RequestBudget) -> Decision:
        if self.cfg.safe_mode_tools_disabled:
            self._audit(tenant_id, actor_ref, tool_name, "deny", "safe_mode_tools_disabled")
            return Decision("deny", "safe_mode_tools_disabled")

        tool = self._get_tool(tool_name)
        if not tool:
            self._audit(tenant_id, actor_ref, tool_name, "deny", "tool_not_registered")
            return Decision("deny", "tool_not_registered")

        scope = tool["scope"]
        if scope not in self._actor_scopes(actor_ref):
            self._audit(tenant_id, actor_ref, tool_name, "deny", "scope_denied")
            return Decision("deny", "scope_denied")

        if self.cfg.safe_mode_finance_write_disabled and scope == "finance:write":
            self._audit(tenant_id, actor_ref, tool_name, "deny", "safe_mode_finance_write_disabled")
            return Decision("deny", "safe_mode_finance_write_disabled")

        if budget.tool_calls >= self.cfg.req_max_tool_calls:
            self._audit(tenant_id, actor_ref, tool_name, "deny", "budget_tool_calls_exhausted")
            return Decision("deny", "budget_tool_calls_exhausted")

        rl = self.ratelimiter.check(f"ratelimit:tool:{actor_ref}", 30, 60)
        if not rl.allowed:
            self._audit(tenant_id, actor_ref, tool_name, "deny", rl.reason)
            return Decision("deny", rl.reason)

        if tool.get("cost_class") == "high" and self._backpressure_high():
            self._audit(tenant_id, actor_ref, tool_name, "deny", "backpressure_high_cost_denied")
            return Decision("deny", "backpressure_high_cost_denied")

        if tool.get("requires_approval"):
            aid = self.db.fetchone_value(
                """
                INSERT INTO approval_requests(tenant_id, actor_ref, action, scope, status, reason_code, request_payload)
                VALUES (%(tenant_id)s, %(actor_ref)s, %(action)s, %(scope)s, 'pending', 'requires_approval', '{}'::jsonb)
                RETURNING id::text;
                """,
                params={"tenant_id": tenant_id, "actor_ref": actor_ref, "action": tool_name, "scope": scope},
            )
            self._audit(tenant_id, actor_ref, tool_name, "pending_approval", "requires_approval", {"approval_id": aid})
            self.db.execute(
                "INSERT INTO observability_events(tenant_id, component, route, event_type, outcome, error_code) VALUES (%(t)s,'governance',%(r)s,'approvals_pending','pending','requires_approval');",
                params={"t": tenant_id, "r": tool_name},
            )
            return Decision("pending_approval", "requires_approval", approval_id=aid)

        budget.tool_calls += 1
        self._audit(tenant_id, actor_ref, tool_name, "allow", "allowed")
        return Decision("allow", "allowed")

    def authorize_job_enqueue(self, *, tenant_id: str, actor_ref: str, budget: RequestBudget) -> Decision:
        if self.cfg.safe_mode_jobs_disabled:
            self._audit(tenant_id, actor_ref, "job_enqueue", "deny", "safe_mode_jobs_disabled")
            return Decision("deny", "safe_mode_jobs_disabled")
        if budget.jobs_enqueued >= self.cfg.req_max_jobs_enqueued:
            self._audit(tenant_id, actor_ref, "job_enqueue", "deny", "budget_jobs_exhausted")
            self.db.execute("INSERT INTO observability_events(tenant_id,component,route,event_type,outcome,error_code) VALUES (%(t)s,'governance','job_enqueue','budget_exhausted','error','jobs');", params={"t": tenant_id})
            return Decision("deny", "budget_jobs_exhausted")
        rl = self.ratelimiter.check(f"ratelimit:job:{actor_ref}", 30, 60)
        if not rl.allowed:
            self._audit(tenant_id, actor_ref, "job_enqueue", "deny", rl.reason)
            return Decision("deny", rl.reason)
        budget.jobs_enqueued += 1
        self._audit(tenant_id, actor_ref, "job_enqueue", "allow", "allowed")
        return Decision("allow", "allowed")
