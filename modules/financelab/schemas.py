from __future__ import annotations

from typing import Any


class FinanceLabSchemaError(ValueError):
    pass


def _require(payload: dict[str, Any], fields: list[str]) -> None:
    missing = [f for f in fields if f not in payload or payload[f] in (None, "")]
    if missing:
        raise FinanceLabSchemaError(f"missing_fields:{','.join(missing)}")


def validate_import_preview_input(payload: dict[str, Any]) -> None:
    _require(payload, ["source_doc_id", "mapping"])


def validate_list_transactions_input(payload: dict[str, Any]) -> None:
    if payload.get("limit") is not None and int(payload["limit"]) <= 0:
        raise FinanceLabSchemaError("limit_must_be_positive")


def validate_spend_summary_input(payload: dict[str, Any]) -> None:
    if payload.get("group_by") not in (None, "category", "merchant"):
        raise FinanceLabSchemaError("group_by_invalid")


def validate_commit_import_input(payload: dict[str, Any]) -> None:
    _require(payload, ["import_id"])


def validate_write_transaction_input(payload: dict[str, Any]) -> None:
    _require(payload, ["ts", "amount"])
