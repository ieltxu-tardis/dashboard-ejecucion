from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from memory_service.db import PostgresExec
from .config import GovernanceConfig


@dataclass
class ApprovalRecord:
    id: str
    tenant_id: str
    actor_ref: str
    action: str
    scope: str
    status: str


def summarize_payload(payload: dict[str, Any]) -> str:
    keys = sorted(payload.keys())
    redacted = {k: ("<redacted>" if any(s in k.lower() for s in ["password", "token", "secret", "authorization", "cookie", "key"]) else type(payload[k]).__name__) for k in keys}
    return json.dumps({"keys": keys[:20], "shape": redacted}, ensure_ascii=False)


def payload_hash(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ApprovalService:
    def __init__(self, db: PostgresExec, cfg: GovernanceConfig):
        self.db = db
        self.cfg = cfg

    def _clean_scalar(self, value: str | None) -> str:
        v = (value or "").strip()
        if not v:
            return ""
        return v.splitlines()[0].strip()

    def expire_pending(self) -> int:
        rows = self.db.fetchall_json(
            """
            SELECT id::text, tenant_id::text
            FROM approval_requests
            WHERE status='pending'
              AND expires_at IS NOT NULL
              AND expires_at <= NOW()
            """
        )
        if not rows:
            return 0
        self.db.execute(
            """
            UPDATE approval_requests
               SET status='expired',
                   decided_at=NOW(),
                   decision_reason='expired_ttl'
             WHERE status='pending'
               AND expires_at IS NOT NULL
               AND expires_at <= NOW();
            """
        )
        for r in rows:
            self.db.execute(
                """
                INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload)
                VALUES (%(t)s, 'system', 'approval-expirer', 'approval.expire', 'approval', %(id)s,
                        jsonb_build_object('reason_code','expired_ttl'));
                """,
                params={"t": r["tenant_id"], "id": r["id"]},
            )
        return len(rows)

    def create_pending(self, *, tenant_id: str, actor_ref: str, action: str, scope: str, request_payload: dict[str, Any]) -> str:
        p_hash = payload_hash(request_payload)
        p_summary = summarize_payload(request_payload)
        aid = self.db.fetchone_value(
            """
            INSERT INTO approval_requests(tenant_id, actor_ref, action, scope, status, reason_code, request_payload, payload_hash, payload_summary, expires_at)
            VALUES (%(tenant_id)s, %(actor_ref)s, %(action)s, %(scope)s, 'pending', 'requires_approval', %(payload)s::jsonb, %(payload_hash)s, %(payload_summary)s, NOW() + (%(ttl)s || ' seconds')::interval)
            RETURNING id::text;
            """,
            params={
                "tenant_id": tenant_id,
                "actor_ref": actor_ref,
                "action": action,
                "scope": scope,
                "payload": request_payload,
                "payload_hash": p_hash,
                "payload_summary": p_summary,
                "ttl": int(self.cfg.approval_ttl_seconds),
            },
        )
        return self._clean_scalar(str(aid))

    def list(self, status: str = "pending", limit: int = 50) -> list[dict[str, Any]]:
        self.expire_pending()
        sql = """
        SELECT id::text, tenant_id::text, actor_ref, action, scope, status, reason_code,
               created_at, decided_at, expires_at, decided_by, decision_reason, payload_hash, payload_summary
        FROM approval_requests
        """
        params: dict[str, Any] = {"limit": int(limit)}
        if status != "all":
            sql += " WHERE status = %(status)s"
            params["status"] = status
        sql += " ORDER BY created_at DESC LIMIT %(limit)s"
        return self.db.fetchall_json(sql, params=params)

    def show(self, approval_id: str) -> dict[str, Any] | None:
        self.expire_pending()
        approval_id = self._clean_scalar(approval_id)
        rows = self.db.fetchall_json(
            """
            SELECT id::text, tenant_id::text, actor_ref, action, scope, status, reason_code,
                   created_at, decided_at, expires_at, decided_by, decision_reason, payload_hash, payload_summary
            FROM approval_requests WHERE id = %(id)s::uuid LIMIT 1
            """,
            params={"id": approval_id},
        )
        return rows[0] if rows else None

    def decide(self, *, approval_id: str, decision: str, decided_by: str, reason: str) -> dict[str, Any]:
        assert decision in {"approved", "denied", "canceled"}
        approval_id = self._clean_scalar(approval_id)
        self.expire_pending()
        current = self.show(approval_id)
        if not current:
            return {"status": "not_found", "approval_id": approval_id}
        if current["status"] in {"approved", "denied", "expired", "canceled"}:
            return {"status": "noop", "approval_id": approval_id, "current_status": current["status"]}

        self.db.execute(
            """
            UPDATE approval_requests
            SET status=%(status)s,
                decided_at=NOW(),
                decided_by=%(decided_by)s,
                decision_reason=%(reason)s
            WHERE id = %(id)s::uuid
            """,
            params={"status": decision, "decided_by": decided_by, "reason": reason[:240], "id": approval_id},
        )
        updated = self.show(approval_id)
        if updated:
            self.db.execute(
                """
                INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload)
                VALUES (%(tenant_id)s, 'admin', %(decided_by)s, %(action)s, 'approval', %(approval_id)s,
                        jsonb_build_object('decision', %(decision)s, 'reason', %(reason)s));
                """,
                params={
                    "tenant_id": updated["tenant_id"],
                    "decided_by": decided_by,
                    "action": f"approval.{decision}",
                    "approval_id": approval_id,
                    "decision": decision,
                    "reason": reason[:240],
                },
            )
        return {"status": "ok", "approval_id": approval_id, "decision": decision}
