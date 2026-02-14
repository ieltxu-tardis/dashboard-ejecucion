from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

from modules.registry import ModuleRegistry
from observability.logging import log_event
from memory_service.service import PostgresMemoryService
from .schemas import (
    validate_capture_task_input,
    validate_list_tasks_input,
    validate_update_task_input,
    validate_capture_goal_input,
    validate_weekly_review_input,
)


class TimeLabService:
    def __init__(self, repo_root: str, memory: PostgresMemoryService):
        self.repo_root = repo_root
        self.memory = memory
        self.modules = ModuleRegistry(repo_root)

    def _ensure_enabled(self) -> None:
        if not self.modules.is_enabled("timelab"):
            raise ValueError("module_disabled:timelab")

    def _clean_id(self, value: str) -> str:
        return str(value).strip().splitlines()[0]

    def capture_task(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_capture_task_input(payload)
        out = self.memory.write_task(
            {
                "tenant_id": tenant_id,
                "actor_ref": actor_ref,
                "intent_type": "explicit_command",
                "reason": "capture task",
                "source": "timelab",
                "scope": "time:write",
                "confidence": 0.95,
                "title": payload["title"],
                "status": payload.get("status", "open"),
                "due_at": payload.get("due_at"),
                "metadata": {
                    "tags": payload.get("tags", []),
                    "priority": payload.get("priority", "normal"),
                },
            }
        )
        log_event("info", "module.timelab", "capture_task", tenant_id=tenant_id)
        return out

    def list_tasks(self, *, tenant_id: str, payload: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        self._ensure_enabled()
        payload = payload or {}
        validate_list_tasks_input(payload)

        filters = ["tenant_id = %(tenant_id)s"]
        params: dict[str, Any] = {"tenant_id": tenant_id, "limit": min(int(payload.get("limit", 50)), 100)}

        if payload.get("status"):
            filters.append("status = %(status)s")
            params["status"] = payload["status"]
        if payload.get("due_from"):
            filters.append("due_at >= %(due_from)s")
            params["due_from"] = payload["due_from"]
        if payload.get("due_to"):
            filters.append("due_at <= %(due_to)s")
            params["due_to"] = payload["due_to"]
        if payload.get("priority"):
            filters.append("metadata->>'priority' = %(priority)s")
            params["priority"] = payload["priority"]
        if payload.get("tag"):
            filters.append("(metadata->'tags') ? %(tag)s")
            params["tag"] = payload["tag"]

        sql = f"""
        SELECT id::text, title, status, due_at, metadata, created_at, updated_at
        FROM tasks
        WHERE {' AND '.join(filters)}
        ORDER BY COALESCE(due_at, created_at) ASC
        LIMIT %(limit)s
        """
        rows = self.memory.db.fetchall_json(sql, params=params)
        log_event("info", "module.timelab", "list_tasks", tenant_id=tenant_id, count=len(rows))
        return rows

    def update_task(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_update_task_input(payload)
        out = self.memory.update_task(
            {
                "tenant_id": tenant_id,
                "actor_ref": actor_ref,
                "intent_type": "explicit_command",
                "reason": "update task",
                "source": "timelab",
                "scope": "time:write",
                "confidence": 0.95,
                "task_id": self._clean_id(payload["task_id"]),
                "title": payload.get("title"),
                "status": payload.get("status"),
                "due_at": payload.get("due_at"),
                "tags": payload.get("tags"),
            }
        )
        log_event("info", "module.timelab", "update_task", tenant_id=tenant_id)
        return out

    def capture_goal(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_capture_goal_input(payload)
        out = self.memory.write_entity(
            {
                "tenant_id": tenant_id,
                "actor_ref": actor_ref,
                "intent_type": "explicit_command",
                "reason": "capture goal",
                "source": "timelab",
                "scope": "time:write",
                "confidence": 0.94,
                "entity_type": "goal",
                "name": payload["title"],
                "attributes": {
                    "notes": payload.get("notes", ""),
                    "status": payload.get("status", "active"),
                    "tags": payload.get("tags", []),
                },
            }
        )
        out["id"] = self._clean_id(out["id"])
        log_event("info", "module.timelab", "capture_goal", tenant_id=tenant_id)
        return out

    def list_goals(self, *, tenant_id: str, limit: int = 50) -> list[dict[str, Any]]:
        self._ensure_enabled()
        rows = self.memory.read_entities(tenant_id, entity_type="goal")[: min(limit, 100)]
        log_event("info", "module.timelab", "list_goals", tenant_id=tenant_id, count=len(rows))
        return rows

    def weekly_review(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        self._ensure_enabled()
        payload = payload or {}
        validate_weekly_review_input(payload)

        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        done = self.memory.db.fetchone_value(
            "SELECT COUNT(*)::text FROM tasks WHERE tenant_id=%(t)s AND status='done' AND updated_at >= %(from)s",
            params={"t": tenant_id, "from": week_ago.isoformat()},
        )
        open_tasks = self.memory.db.fetchone_value(
            "SELECT COUNT(*)::text FROM tasks WHERE tenant_id=%(t)s AND status='open'",
            params={"t": tenant_id},
        )
        blockers = self.memory.db.fetchone_value(
            "SELECT COUNT(*)::text FROM tasks WHERE tenant_id=%(t)s AND status='blocked'",
            params={"t": tenant_id},
        )
        summary = {
            "window": {"from": week_ago.isoformat(), "to": now.isoformat()},
            "completed": int(done or "0"),
            "open": int(open_tasks or "0"),
            "blockers": int(blockers or "0"),
        }

        persisted = False
        doc_id = None
        if payload.get("persist", False):
            content = f"Weekly review: completed={summary['completed']} open={summary['open']} blockers={summary['blockers']}"
            chash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            out = self.memory.write_document(
                {
                    "tenant_id": tenant_id,
                    "actor_ref": actor_ref,
                    "intent_type": "explicit_command",
                    "reason": "weekly review persist",
                    "source": "timelab",
                    "scope": "time:write",
                    "confidence": 0.9,
                    "source_type": "weekly_review",
                    "source_ref": f"week:{now.date().isoformat()}",
                    "content": content,
                    "content_hash": chash,
                    "metadata": {"module": "timelab", "summary": summary},
                }
            )
            doc_id = self._clean_id(out["id"])
            persisted = True

        log_event("info", "module.timelab", "weekly_review", tenant_id=tenant_id, persisted=persisted)
        return {"summary": summary, "persisted": persisted, "document_id": doc_id}
