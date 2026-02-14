from typing import Any, Dict


class SchemaValidationError(ValueError):
    pass


REQUIRED_COMMON = ["tenant_id", "actor_ref", "intent_type", "reason", "source", "scope", "confidence"]


def _require_fields(payload: Dict[str, Any], fields: list[str]) -> None:
    missing = [f for f in fields if f not in payload or payload[f] in (None, "")]
    if missing:
        raise SchemaValidationError(f"missing_fields:{','.join(missing)}")


def validate_document_write(payload: Dict[str, Any]) -> None:
    _require_fields(payload, REQUIRED_COMMON + ["source_type", "content", "content_hash"])


def validate_entity_write(payload: Dict[str, Any]) -> None:
    _require_fields(payload, REQUIRED_COMMON + ["entity_type", "name"])


def validate_fact_write(payload: Dict[str, Any]) -> None:
    _require_fields(payload, REQUIRED_COMMON + ["key", "value"])
