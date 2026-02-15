from __future__ import annotations

from typing import Any


class DigestHubSchemaError(ValueError):
    pass


def _require(payload: dict[str, Any], fields: list[str]) -> None:
    missing = [f for f in fields if f not in payload or payload[f] in (None, "")]
    if missing:
        raise DigestHubSchemaError(f"missing_fields:{','.join(missing)}")


def validate_subscribe_daily(payload: dict[str, Any]) -> None:
    _require(payload, ["actor_id"])


def validate_subscribe_weekly(payload: dict[str, Any]) -> None:
    _require(payload, ["actor_id"])


def validate_unsubscribe(payload: dict[str, Any]) -> None:
    _require(payload, ["actor_id", "period"])


def validate_preview(payload: dict[str, Any]) -> None:
    _require(payload, ["actor_id"])


def validate_send_now(payload: dict[str, Any]) -> None:
    _require(payload, ["actor_id", "period"])
