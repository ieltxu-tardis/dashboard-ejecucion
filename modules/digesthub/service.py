from __future__ import annotations

import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from memory_service.service import PostgresMemoryService
from modules.registry import ModuleRegistry
from observability.logging import log_event

from .schemas import (
    validate_preview,
    validate_send_now,
    validate_subscribe_daily,
    validate_subscribe_weekly,
    validate_unsubscribe,
)


class DigestHubService:
    def __init__(self, repo_root: str, memory: PostgresMemoryService):
        self.repo_root = repo_root
        self.memory = memory
        self.modules = ModuleRegistry(repo_root)

    def _ensure_enabled(self) -> None:
        if not self.modules.is_enabled("digesthub"):
            raise ValueError("module_disabled:digesthub")

    def _clean(self, v: str) -> str:
        return str(v).strip().splitlines()[0]

    def _upsert_sub(self, *, tenant_id: str, actor_id: str, period: str, timezone_name: str, schedule: dict[str, Any]) -> str:
        existing = self.memory.db.fetchone_value(
            "SELECT id::text FROM digest_subscriptions WHERE tenant_id=%(t)s AND actor_id=%(a)s AND period=%(p)s LIMIT 1",
            params={"t": tenant_id, "a": actor_id, "p": period},
        )
        if existing:
            sid = self._clean(existing)
            self.memory.db.execute(
                """
                UPDATE digest_subscriptions
                SET enabled=TRUE, delivery_mode='dm', timezone=%(tz)s, schedule=%(s)s::jsonb, updated_at=NOW()
                WHERE id=%(id)s::uuid AND tenant_id=%(t)s
                """,
                params={"id": sid, "t": tenant_id, "tz": timezone_name, "s": schedule},
            )
            return sid
        sid = self.memory.db.fetchone_value(
            """
            INSERT INTO digest_subscriptions(tenant_id, actor_id, delivery_mode, timezone, period, schedule, enabled)
            VALUES (%(t)s, %(a)s, 'dm', %(tz)s, %(p)s, %(s)s::jsonb, TRUE)
            RETURNING id::text;
            """,
            params={"t": tenant_id, "a": actor_id, "tz": timezone_name, "p": period, "s": schedule},
        )
        return self._clean(sid or "")

    def subscribe_daily(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_subscribe_daily(payload)
        sid = self._upsert_sub(
            tenant_id=tenant_id,
            actor_id=payload["actor_id"],
            period="daily",
            timezone_name=payload.get("timezone", os.getenv("DIGESTHUB_DEFAULT_TZ", "UTC")),
            schedule={"hour": int(payload.get("hour", int(os.getenv("DIGESTHUB_DAILY_HOUR_UTC", "9"))))},
        )
        self.memory.db.execute(
            "INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload) VALUES (%(t)s,'user',%(a)s,'digesthub.subscribe_daily','digest_subscription',%(id)s,jsonb_build_object('mode','dm'));",
            params={"t": tenant_id, "a": actor_ref, "id": sid},
        )
        return {"subscription_id": sid, "period": "daily", "delivery_mode": "dm"}

    def subscribe_weekly(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_subscribe_weekly(payload)
        sid = self._upsert_sub(
            tenant_id=tenant_id,
            actor_id=payload["actor_id"],
            period="weekly",
            timezone_name=payload.get("timezone", os.getenv("DIGESTHUB_DEFAULT_TZ", "UTC")),
            schedule={
                "weekday": int(payload.get("weekday", int(os.getenv("DIGESTHUB_WEEKLY_WEEKDAY", "1")))),
                "hour": int(payload.get("hour", int(os.getenv("DIGESTHUB_WEEKLY_HOUR_UTC", "10")))),
            },
        )
        self.memory.db.execute(
            "INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload) VALUES (%(t)s,'user',%(a)s,'digesthub.subscribe_weekly','digest_subscription',%(id)s,jsonb_build_object('mode','dm'));",
            params={"t": tenant_id, "a": actor_ref, "id": sid},
        )
        return {"subscription_id": sid, "period": "weekly", "delivery_mode": "dm"}

    def unsubscribe(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_unsubscribe(payload)
        self.memory.db.execute(
            "UPDATE digest_subscriptions SET enabled=FALSE, updated_at=NOW() WHERE tenant_id=%(t)s AND actor_id=%(a)s AND period=%(p)s",
            params={"t": tenant_id, "a": payload["actor_id"], "p": payload["period"]},
        )
        self.memory.db.execute(
            "INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload) VALUES (%(t)s,'user',%(ar)s,'digesthub.unsubscribe','digest_subscription',%(actor)s,jsonb_build_object('period',%(p)s));",
            params={"t": tenant_id, "ar": actor_ref, "actor": payload["actor_id"], "p": payload["period"]},
        )
        return {"ok": True}

    def _build_sections(self, tenant_id: str) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        tomorrow = now + timedelta(days=1)
        week_ago = now - timedelta(days=7)

        time_section = {
            "due_soon": int(self.memory.db.fetchone_value("SELECT COUNT(*)::text FROM tasks WHERE tenant_id=%(t)s AND status='open' AND due_at IS NOT NULL AND due_at <= %(tom)s", params={"t": tenant_id, "tom": tomorrow.isoformat()}) or "0"),
            "overdue": int(self.memory.db.fetchone_value("SELECT COUNT(*)::text FROM tasks WHERE tenant_id=%(t)s AND status='open' AND due_at < NOW()", params={"t": tenant_id}) or "0"),
            "recent_done": int(self.memory.db.fetchone_value("SELECT COUNT(*)::text FROM tasks WHERE tenant_id=%(t)s AND status='done' AND updated_at >= %(w)s", params={"t": tenant_id, "w": week_ago.isoformat()}) or "0"),
        }

        finance_rows = self.memory.db.fetchall_json(
            """
            SELECT COALESCE(category,'uncategorized') AS bucket, SUM(amount)::float8 AS total
            FROM finance_transactions
            WHERE tenant_id=%(t)s AND ts >= %(w)s
            GROUP BY 1 ORDER BY total DESC LIMIT 3
            """,
            params={"t": tenant_id, "w": week_ago.isoformat()},
        )
        finance_section = {"top_categories": finance_rows}

        idea_recent = int(self.memory.db.fetchone_value("SELECT COUNT(*)::text FROM entities WHERE tenant_id=%(t)s AND type='idea' AND created_at >= %(w)s", params={"t": tenant_id, "w": week_ago.isoformat()}) or "0")
        idea_top = self.memory.db.fetchall_json(
            """
            SELECT value->>'idea_id' AS idea_id, (value->'rubric'->>'score')::float8 AS score
            FROM facts
            WHERE tenant_id=%(t)s AND key='idealab.evaluation'
            ORDER BY score DESC NULLS LAST
            LIMIT 3
            """,
            params={"t": tenant_id},
        )
        idea_section = {"recent_ideas": idea_recent, "top_evaluated": idea_top}

        research_recent = int(self.memory.db.fetchone_value("SELECT COUNT(*)::text FROM documents WHERE tenant_id=%(t)s AND source_type IN ('research_note','digest') AND created_at >= %(w)s", params={"t": tenant_id, "w": week_ago.isoformat()}) or "0")
        suggested_searches = ["open overdue tasks", "top spend categories", "recent research notes"]
        research_section = {"recent_docs": research_recent, "suggested_searches": suggested_searches}

        return {
            "timelab": time_section,
            "financelab": finance_section,
            "idealab": idea_section,
            "researchlab": research_section,
        }

    def preview_daily(self, *, tenant_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_preview(payload)
        sections = self._build_sections(tenant_id)
        degraded = int(self.memory.db.fetchone_value("SELECT COUNT(*)::text FROM jobs WHERE status='queued'", params={}) or "0") > int(os.getenv("DIGESTHUB_BACKLOG_THRESHOLD", "50"))
        text = self._render_text(sections, degraded=degraded, period="daily")
        return {"period": "daily", "degraded": degraded, "sections": sections, "text": text}

    def _render_text(self, sections: dict[str, Any], *, degraded: bool, period: str) -> str:
        if degraded:
            return f"{period.title()} Digest (short): overdue={sections['timelab']['overdue']} due_soon={sections['timelab']['due_soon']} top_spend={len(sections['financelab']['top_categories'])}"
        return (
            f"{period.title()} Digest\n"
            f"- TimeLab: due_soon={sections['timelab']['due_soon']}, overdue={sections['timelab']['overdue']}, done_recent={sections['timelab']['recent_done']}\n"
            f"- FinanceLab top categories: {sections['financelab']['top_categories']}\n"
            f"- IdeaLab: recent={sections['idealab']['recent_ideas']} top={sections['idealab']['top_evaluated']}\n"
            f"- ResearchLab: recent_docs={sections['researchlab']['recent_docs']} suggested={sections['researchlab']['suggested_searches']}"
        )

    def send_now(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_send_now(payload)
        period = payload["period"]
        sections = self._build_sections(tenant_id)
        degraded = int(self.memory.db.fetchone_value("SELECT COUNT(*)::text FROM jobs WHERE status='queued'", params={}) or "0") > int(os.getenv("DIGESTHUB_BACKLOG_THRESHOLD", "50"))
        text = self._render_text(sections, degraded=degraded, period=period)

        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        sub = self.memory.db.fetchone_value(
            "SELECT id::text FROM digest_subscriptions WHERE tenant_id=%(t)s AND actor_id=%(a)s AND period=%(p)s AND enabled=TRUE LIMIT 1",
            params={"t": tenant_id, "a": payload["actor_id"], "p": period},
        )
        if not sub:
            sid = self._upsert_sub(tenant_id=tenant_id, actor_id=payload["actor_id"], period=period, timezone_name="UTC", schedule={"hour": 9})
        else:
            sid = self._clean(sub)

        self.memory.db.execute(
            """
            INSERT INTO digest_deliveries(tenant_id, subscription_id, period, content_hash, status, summary)
            VALUES (%(t)s, %(s)s::uuid, %(p)s, %(h)s, 'simulated_sent', jsonb_build_object('degraded', %(d)s, 'chars', %(c)s));
            """,
            params={"t": tenant_id, "s": sid, "p": period, "h": content_hash, "d": degraded, "c": len(text)},
        )
        self.memory.db.execute(
            "UPDATE digest_subscriptions SET last_sent_at=NOW(), updated_at=NOW() WHERE tenant_id=%(t)s AND id=%(s)s::uuid",
            params={"t": tenant_id, "s": sid},
        )
        self.memory.db.execute(
            "INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload) VALUES (%(t)s,'user',%(a)s,'digesthub.send_now','digest_subscription',%(s)s,jsonb_build_object('period',%(p)s,'hash',%(h)s,'mode','dm_simulated'));",
            params={"t": tenant_id, "a": actor_ref, "s": sid, "p": period, "h": content_hash},
        )
        log_event("info", "module.digesthub", "send_now", tenant_id=tenant_id, period=period)
        return {"status": "ok", "delivery_mode": "dm", "subscription_id": sid, "content_hash": content_hash, "text": text}

    def tick_due(self, *, tenant_id: str, now_utc: datetime | None = None) -> dict[str, Any]:
        self._ensure_enabled()
        now_utc = now_utc or datetime.now(timezone.utc)
        rows = self.memory.db.fetchall_json(
            "SELECT id::text, actor_id, period, schedule, last_sent_at FROM digest_subscriptions WHERE tenant_id=%(t)s AND enabled=TRUE AND delivery_mode='dm'",
            params={"t": tenant_id},
        )
        sent = 0
        for r in rows:
            period = r["period"]
            schedule = r.get("schedule") or {}
            if period == "daily" and now_utc.hour == int(schedule.get("hour", 9)):
                self.send_now(tenant_id=tenant_id, actor_ref="digest-scheduler", payload={"actor_id": r["actor_id"], "period": "daily"})
                sent += 1
            if period == "weekly" and now_utc.weekday() == int(schedule.get("weekday", 1)) and now_utc.hour == int(schedule.get("hour", 10)):
                self.send_now(tenant_id=tenant_id, actor_ref="digest-scheduler", payload={"actor_id": r["actor_id"], "period": "weekly"})
                sent += 1
        return {"sent": sent, "checked": len(rows)}
