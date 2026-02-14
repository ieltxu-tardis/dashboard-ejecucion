from __future__ import annotations

from typing import Any


class TimeLabSchemaError(ValueError):
    pass


def _require(payload: dict[str, Any], fields: list[str]) -> None:
    missing = [f for f in fields if f not in payload or payload[f] in (None, "")]
    if missing:
        raise TimeLabSchemaError(f"missing_fields:{','.join(missing)}")


def validate_capture_task_input(payload: dict[str, Any]) -> None:
    _require(payload, ["title"])


def validate_list_tasks_input(payload: dict[str, Any]) -> None:
    if payload.get("limit") is not None and int(payload["limit"]) <= 0:
        raise TimeLabSchemaError("limit_must_be_positive")


def validate_update_task_input(payload: dict[str, Any]) -> None:
    _require(payload, ["task_id"])


def validate_capture_goal_input(payload: dict[str, Any]) -> None:
    _require(payload, ["title"])


def validate_weekly_review_input(payload: dict[str, Any]) -> None:
    # optional persist bool
    if "persist" in payload and not isinstance(payload["persist"], bool):
        raise TimeLabSchemaError("persist_must_be_boolean")
