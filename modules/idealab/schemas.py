from __future__ import annotations

from typing import Any


class IdeaLabSchemaError(ValueError):
    pass


def _require(payload: dict[str, Any], fields: list[str]) -> None:
    missing = [f for f in fields if f not in payload or payload[f] in (None, "")]
    if missing:
        raise IdeaLabSchemaError(f"missing_fields:{','.join(missing)}")


def validate_capture_idea_input(payload: dict[str, Any]) -> None:
    _require(payload, ["title", "summary"])


def validate_list_ideas_input(payload: dict[str, Any]) -> None:
    if payload.get("limit") is not None and int(payload["limit"]) <= 0:
        raise IdeaLabSchemaError("limit_must_be_positive")


def validate_evaluate_idea_input(payload: dict[str, Any]) -> None:
    _require(payload, ["idea_id"])


def validate_plan_experiment_input(payload: dict[str, Any]) -> None:
    _require(payload, ["idea_id", "hypothesis", "metric", "plan"])


def validate_log_experiment_result_input(payload: dict[str, Any]) -> None:
    _require(payload, ["experiment_id", "result"])
