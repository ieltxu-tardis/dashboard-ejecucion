from __future__ import annotations

from typing import Any

from observability.logging import log_event
from modules.registry import ModuleRegistry
from memory_service.service import PostgresMemoryService
from .schemas import (
    validate_capture_idea_input,
    validate_list_ideas_input,
    validate_evaluate_idea_input,
    validate_plan_experiment_input,
    validate_log_experiment_result_input,
)


class IdeaLabService:
    def __init__(self, repo_root: str, memory: PostgresMemoryService):
        self.repo_root = repo_root
        self.memory = memory
        self.modules = ModuleRegistry(repo_root)

    def _clean_id(self, value: str) -> str:
        return str(value).strip().splitlines()[0]

    def _ensure_enabled(self) -> None:
        if not self.modules.is_enabled("idealab"):
            raise ValueError("module_disabled:idealab")

    def capture_idea(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_capture_idea_input(payload)
        out = self.memory.write_entity(
            {
                "tenant_id": tenant_id,
                "actor_ref": actor_ref,
                "intent_type": "explicit_command",
                "reason": "capture idea",
                "source": "idealab",
                "scope": "ideas:write",
                "confidence": 0.95,
                "entity_type": "idea",
                "name": payload["title"],
                "attributes": {
                    "summary": payload["summary"],
                    "tags": payload.get("tags", []),
                    "status": payload.get("status", "new"),
                },
            }
        )
        out["id"] = self._clean_id(out["id"])
        log_event("info", "module.idealab", "capture_idea", tenant_id=tenant_id)
        return out

    def list_ideas(self, *, tenant_id: str, payload: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        self._ensure_enabled()
        payload = payload or {}
        validate_list_ideas_input(payload)
        limit = min(int(payload.get("limit", 20)), 100)
        rows = self.memory.db.fetchall_json(
            """
            SELECT id::text, name as title, attributes, created_at, updated_at
            FROM entities
            WHERE tenant_id = %(tenant_id)s
              AND type = 'idea'
            ORDER BY created_at DESC
            LIMIT %(limit)s
            """,
            params={"tenant_id": tenant_id, "limit": limit},
        )
        log_event("info", "module.idealab", "list_ideas", tenant_id=tenant_id, count=len(rows))
        return rows

    def evaluate_idea(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_evaluate_idea_input(payload)
        idea_id = self._clean_id(payload["idea_id"])
        idea = self.memory.db.fetchall_json(
            """
            SELECT id::text, name, attributes
            FROM entities
            WHERE tenant_id = %(tenant_id)s
              AND id = %(idea_id)s::uuid
              AND type = 'idea'
            LIMIT 1
            """,
            params={"tenant_id": tenant_id, "idea_id": idea_id},
        )
        if not idea:
            raise ValueError("idea_not_found")
        i = idea[0]
        attrs = i.get("attributes") or {}
        summary = str(attrs.get("summary", ""))
        tags = attrs.get("tags", []) if isinstance(attrs.get("tags", []), list) else []

        novelty = min(5, max(1, 2 + len(set(tags))))
        feasibility = 4 if len(summary) < 400 else 3
        impact = 4 if any(t in ["growth", "revenue", "retention"] for t in tags) else 3
        score = round((novelty + feasibility + impact) / 3, 2)

        rubric = {
            "novelty": novelty,
            "feasibility": feasibility,
            "impact": impact,
            "score": score,
            "notes": "Auto-rubric MVP (heuristic).",
        }

        self.memory.write_fact(
            {
                "tenant_id": tenant_id,
                "actor_ref": actor_ref,
                "intent_type": "explicit_command",
                "reason": "idea evaluation",
                "source": "idealab",
                "scope": "ideas:write",
                "confidence": 0.9,
                "key": "idealab.evaluation",
                "value": {"idea_id": i["id"], "rubric": rubric},
                "source_doc_id": None,
            }
        )
        self.memory.write_event(
            {
                "tenant_id": tenant_id,
                "actor_ref": actor_ref,
                "intent_type": "explicit_command",
                "reason": "idea evaluated",
                "source": "idealab",
                "scope": "ideas:write",
                "confidence": 0.9,
                "event_type": "idealab.idea_evaluated",
                "payload": {"idea_id": i["id"], "score": score},
                "source_doc_id": None,
            }
        )
        log_event("info", "module.idealab", "evaluate_idea", tenant_id=tenant_id, score=score)
        return {"idea_id": i["id"], "rubric": rubric}

    def plan_experiment(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_plan_experiment_input(payload)
        idea_id = self._clean_id(payload["idea_id"])
        out = self.memory.write_entity(
            {
                "tenant_id": tenant_id,
                "actor_ref": actor_ref,
                "intent_type": "explicit_command",
                "reason": "plan experiment",
                "source": "idealab",
                "scope": "ideas:write",
                "confidence": 0.94,
                "entity_type": "experiment",
                "name": f"experiment:{idea_id}",
                "attributes": {
                    "idea_id": idea_id,
                    "hypothesis": payload["hypothesis"],
                    "metric": payload["metric"],
                    "plan": payload["plan"],
                    "result": None,
                },
            }
        )
        out["id"] = self._clean_id(out["id"])
        log_event("info", "module.idealab", "plan_experiment", tenant_id=tenant_id)
        return out

    def log_experiment_result(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_log_experiment_result_input(payload)
        experiment_id = self._clean_id(payload["experiment_id"])
        self.memory.db.execute(
            """
            UPDATE entities
            SET attributes = attributes || jsonb_build_object('result', %(result)s),
                updated_at = NOW()
            WHERE tenant_id = %(tenant_id)s
              AND id = %(experiment_id)s::uuid
              AND type = 'experiment'
            """,
            params={"tenant_id": tenant_id, "experiment_id": experiment_id, "result": payload["result"]},
        )
        self.memory.write_event(
            {
                "tenant_id": tenant_id,
                "actor_ref": actor_ref,
                "intent_type": "explicit_command",
                "reason": "experiment result logged",
                "source": "idealab",
                "scope": "ideas:write",
                "confidence": 0.9,
                "event_type": "idealab.experiment_result",
                "payload": {"experiment_id": experiment_id},
                "source_doc_id": None,
            }
        )
        log_event("info", "module.idealab", "log_experiment_result", tenant_id=tenant_id)
        return {"ok": True, "experiment_id": experiment_id}
