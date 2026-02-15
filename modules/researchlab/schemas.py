from __future__ import annotations

from typing import Any


class ResearchLabSchemaError(ValueError):
    pass


def _require(payload: dict[str, Any], fields: list[str]) -> None:
    missing = [f for f in fields if f not in payload or payload[f] in (None, "")]
    if missing:
        raise ResearchLabSchemaError(f"missing_fields:{','.join(missing)}")


def validate_ingest_note_input(payload: dict[str, Any]) -> None:
    _require(payload, ["content"])


def validate_create_collection_input(payload: dict[str, Any]) -> None:
    _require(payload, ["name"])


def validate_add_to_collection_input(payload: dict[str, Any]) -> None:
    _require(payload, ["collection_id", "doc_id"])


def validate_search_input(payload: dict[str, Any]) -> None:
    _require(payload, ["query_text"])
    if payload.get("top_k") is not None and int(payload["top_k"]) <= 0:
        raise ResearchLabSchemaError("top_k_must_be_positive")
