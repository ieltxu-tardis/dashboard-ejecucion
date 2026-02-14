from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from governance.engine import RequestBudget
from governance.tool_runner import ToolRunner
from memory_service.service import PostgresMemoryService
from modules.registry import ModuleRegistry
from observability.logging import log_event

from .schemas import (
    validate_commit_import_input,
    validate_import_preview_input,
    validate_list_transactions_input,
    validate_spend_summary_input,
    validate_write_transaction_input,
)


class FinanceLabService:
    def __init__(self, repo_root: str, memory: PostgresMemoryService):
        self.repo_root = repo_root
        self.memory = memory
        self.modules = ModuleRegistry(repo_root)
        self.runner = ToolRunner(repo_root)

    def _ensure_enabled(self) -> None:
        if not self.modules.is_enabled("financelab"):
            raise ValueError("module_disabled:financelab")

    def _clean_id(self, value: str) -> str:
        return str(value).strip().splitlines()[0]

    def _parse_csv(self, content: str, mapping: dict[str, str]) -> list[dict[str, Any]]:
        rdr = csv.DictReader(io.StringIO(content))
        rows: list[dict[str, Any]] = []
        for raw in rdr:
            ts = str(raw.get(mapping.get("date", "date"), "")).strip()
            amt = str(raw.get(mapping.get("amount", "amount"), "")).strip()
            merchant = str(raw.get(mapping.get("merchant", "merchant"), "")).strip()
            category = str(raw.get(mapping.get("category", "category"), "")).strip() or None
            note_col = mapping.get("note")
            note = str(raw.get(note_col, "")).strip() if note_col else None
            if not ts or not amt:
                continue
            rows.append(
                {
                    "ts": ts,
                    "amount": Decimal(amt),
                    "merchant": merchant or None,
                    "category": category,
                    "note": note,
                }
            )
        return rows

    def _row_hash(self, row: dict[str, Any], currency: str) -> str:
        payload = f"{row['ts']}|{row['amount']}|{row.get('merchant') or ''}|{row.get('note') or ''}|{currency}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def import_preview_csv(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_import_preview_input(payload)
        source_doc_id = self._clean_id(payload["source_doc_id"])
        mapping = payload["mapping"]
        currency = payload.get("currency", os.getenv("FINANCE_DEFAULT_CURRENCY", "USD"))

        doc_rows = self.memory.db.fetchall_json(
            "SELECT id::text, content FROM documents WHERE tenant_id=%(t)s AND id=%(d)s::uuid LIMIT 1",
            params={"t": tenant_id, "d": source_doc_id},
        )
        if not doc_rows:
            raise ValueError("source_document_not_found")
        content = doc_rows[0]["content"]

        rows = self._parse_csv(content, mapping)
        max_rows = int(os.getenv("FINANCE_IMPORT_MAX_ROWS", "1000"))
        rows = rows[:max_rows]

        norm = [
            {
                "ts": r["ts"],
                "amount": str(r["amount"]),
                "merchant": r.get("merchant"),
                "category": r.get("category"),
                "note": r.get("note"),
            }
            for r in rows
        ]
        payload_hash = hashlib.sha256(json.dumps(norm, sort_keys=True).encode("utf-8")).hexdigest()

        total = sum((r["amount"] for r in rows), Decimal("0"))
        sample = [
            {
                "ts": r["ts"],
                "amount": float(r["amount"]),
                "merchant_hash": hashlib.sha256((r.get("merchant") or "").encode("utf-8")).hexdigest()[:12],
                "category": r.get("category"),
            }
            for r in rows[:5]
        ]
        summary = {
            "count": len(rows),
            "total": float(total),
            "currency": currency,
            "sample": sample,
        }

        import_id = self.memory.db.fetchone_value(
            """
            INSERT INTO finance_imports(tenant_id, source_doc_id, status, payload_hash, summary, metadata)
            VALUES (%(t)s, %(d)s::uuid, 'previewed', %(h)s, %(s)s::jsonb,
                    jsonb_build_object('mapping', %(m)s::jsonb, 'currency', %(c)s))
            RETURNING id::text;
            """,
            params={"t": tenant_id, "d": source_doc_id, "h": payload_hash, "s": summary, "m": mapping, "c": currency},
        )

        self.memory.db.execute(
            """
            INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload)
            VALUES (%(t)s, 'user', %(a)s, 'financelab.import_preview_csv', 'finance_import', %(i)s,
                    jsonb_build_object('count', %(count)s, 'currency', %(currency)s, 'payload_hash', %(h)s));
            """,
            params={"t": tenant_id, "a": actor_ref, "i": self._clean_id(import_id), "count": len(rows), "currency": currency, "h": payload_hash},
        )
        log_event("info", "module.financelab", "import_preview_csv", tenant_id=tenant_id, count=len(rows))
        return {"import_id": self._clean_id(import_id), "payload_hash": payload_hash, "summary": summary}

    def list_transactions(self, *, tenant_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        self._ensure_enabled()
        payload = payload or {}
        validate_list_transactions_input(payload)
        limit = min(int(payload.get("limit", 50)), 200)
        cursor = payload.get("cursor")

        filters = ["tenant_id = %(t)s"]
        params: dict[str, Any] = {"t": tenant_id, "limit": limit}
        if payload.get("from_ts"):
            filters.append("ts >= %(from_ts)s")
            params["from_ts"] = payload["from_ts"]
        if payload.get("to_ts"):
            filters.append("ts <= %(to_ts)s")
            params["to_ts"] = payload["to_ts"]
        if payload.get("category"):
            filters.append("category = %(category)s")
            params["category"] = payload["category"]
        if payload.get("merchant"):
            filters.append("merchant ILIKE %(merchant_like)s")
            params["merchant_like"] = f"%{payload['merchant']}%"
        if cursor:
            filters.append("created_at < %(cursor)s::timestamptz")
            params["cursor"] = cursor

        rows = self.memory.db.fetchall_json(
            f"""
            SELECT id::text, ts, amount, currency, category,
                   CASE WHEN merchant IS NULL THEN NULL ELSE left(merchant, 24) END AS merchant,
                   created_at
            FROM finance_transactions
            WHERE {' AND '.join(filters)}
            ORDER BY created_at DESC
            LIMIT %(limit)s
            """,
            params=params,
        )
        next_cursor = rows[-1]["created_at"] if rows else None
        return {"items": rows, "next_cursor": next_cursor}

    def spend_summary(self, *, tenant_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        self._ensure_enabled()
        payload = payload or {}
        validate_spend_summary_input(payload)
        group_by = payload.get("group_by", "category")

        filters = ["tenant_id = %(t)s"]
        params: dict[str, Any] = {"t": tenant_id}
        if payload.get("from_ts"):
            filters.append("ts >= %(from_ts)s")
            params["from_ts"] = payload["from_ts"]
        if payload.get("to_ts"):
            filters.append("ts <= %(to_ts)s")
            params["to_ts"] = payload["to_ts"]

        col = "category" if group_by == "category" else "merchant"
        rows = self.memory.db.fetchall_json(
            f"""
            SELECT COALESCE({col}, 'uncategorized') AS bucket,
                   COUNT(*)::int AS tx_count,
                   SUM(amount)::float8 AS total
            FROM finance_transactions
            WHERE {' AND '.join(filters)}
            GROUP BY 1
            ORDER BY total DESC NULLS LAST
            LIMIT 100
            """,
            params=params,
        )
        grand = sum(float(r.get("total") or 0.0) for r in rows)
        return {"group_by": group_by, "total": grand, "rows": rows}

    def commit_import(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_commit_import_input(payload)
        import_id = self._clean_id(payload["import_id"])

        auth = self.runner.run_tool(
            tenant_id=tenant_id,
            actor_ref=actor_ref,
            tool_name="financelab.commit_import",
            payload={"import_id": import_id},
            budget=RequestBudget(),
            approval_id=payload.get("approval_id"),
        )
        if auth.status != "allow":
            return {"status": auth.status, "reason_code": auth.reason_code, "approval_id": auth.approval_id}

        imp_rows = self.memory.db.fetchall_json(
            "SELECT id::text, source_doc_id::text, status, payload_hash, metadata FROM finance_imports WHERE tenant_id=%(t)s AND id=%(i)s::uuid LIMIT 1",
            params={"t": tenant_id, "i": import_id},
        )
        if not imp_rows:
            raise ValueError("import_not_found")
        imp = imp_rows[0]
        if imp["status"] == "committed":
            return {"status": "ok", "import_id": import_id, "inserted": 0, "deduped": 0}

        doc = self.memory.db.fetchall_json(
            "SELECT content FROM documents WHERE tenant_id=%(t)s AND id=%(d)s::uuid LIMIT 1",
            params={"t": tenant_id, "d": imp["source_doc_id"]},
        )
        if not doc:
            raise ValueError("source_document_not_found")

        metadata = imp.get("metadata") or {}
        mapping = metadata.get("mapping") or {}
        currency = metadata.get("currency") or os.getenv("FINANCE_DEFAULT_CURRENCY", "USD")
        rows = self._parse_csv(doc[0]["content"], mapping)
        norm = [{"ts": r["ts"], "amount": str(r["amount"]), "merchant": r.get("merchant"), "category": r.get("category"), "note": r.get("note")} for r in rows]
        payload_hash = hashlib.sha256(json.dumps(norm, sort_keys=True).encode("utf-8")).hexdigest()
        if payload_hash != imp["payload_hash"]:
            raise ValueError("payload_hash_mismatch")

        inserted = 0
        deduped = 0
        for r in rows:
            h = self._row_hash(r, currency)
            before = self.memory.db.fetchone_value(
                "SELECT COUNT(*)::text FROM finance_transactions WHERE tenant_id=%(t)s AND external_id_or_hash=%(h)s",
                params={"t": tenant_id, "h": h},
            )
            self.memory.db.execute(
                """
                INSERT INTO finance_transactions(tenant_id, ts, amount, currency, category, merchant, note, external_id_or_hash, metadata)
                VALUES (%(t)s, %(ts)s::timestamptz, %(amount)s, %(currency)s, %(category)s, %(merchant)s, %(note)s, %(h)s,
                        jsonb_build_object('import_id', %(import_id)s))
                ON CONFLICT (tenant_id, external_id_or_hash) DO NOTHING;
                """,
                params={
                    "t": tenant_id,
                    "ts": r["ts"],
                    "amount": float(r["amount"]),
                    "currency": currency,
                    "category": r.get("category"),
                    "merchant": r.get("merchant"),
                    "note": r.get("note"),
                    "h": h,
                    "import_id": import_id,
                },
            )
            after = self.memory.db.fetchone_value(
                "SELECT COUNT(*)::text FROM finance_transactions WHERE tenant_id=%(t)s AND external_id_or_hash=%(h)s",
                params={"t": tenant_id, "h": h},
            )
            if int(after or "0") > int(before or "0"):
                inserted += 1
            else:
                deduped += 1

        self.memory.db.execute(
            "UPDATE finance_imports SET status='committed', updated_at=NOW() WHERE tenant_id=%(t)s AND id=%(i)s::uuid",
            params={"t": tenant_id, "i": import_id},
        )
        self.memory.db.execute(
            """
            INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload)
            VALUES (%(t)s, 'user', %(a)s, 'financelab.commit_import', 'finance_import', %(i)s,
                    jsonb_build_object('inserted', %(ins)s, 'deduped', %(ded)s, 'payload_hash', %(h)s));
            """,
            params={"t": tenant_id, "a": actor_ref, "i": import_id, "ins": inserted, "ded": deduped, "h": payload_hash},
        )
        log_event("info", "module.financelab", "commit_import", tenant_id=tenant_id, inserted=inserted, deduped=deduped)
        return {"status": "ok", "import_id": import_id, "inserted": inserted, "deduped": deduped}

    def write_transaction(self, *, tenant_id: str, actor_ref: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_enabled()
        validate_write_transaction_input(payload)
        auth = self.runner.run_tool(
            tenant_id=tenant_id,
            actor_ref=actor_ref,
            tool_name="financelab.write_transaction",
            payload={"ts": payload["ts"], "amount": payload["amount"]},
            budget=RequestBudget(),
            approval_id=payload.get("approval_id"),
        )
        if auth.status != "allow":
            return {"status": auth.status, "reason_code": auth.reason_code, "approval_id": auth.approval_id}

        currency = payload.get("currency", os.getenv("FINANCE_DEFAULT_CURRENCY", "USD"))
        row = {
            "ts": payload["ts"],
            "amount": Decimal(str(payload["amount"])),
            "merchant": payload.get("merchant"),
            "note": payload.get("note"),
        }
        h = self._row_hash(row, currency)
        tx_id = self.memory.db.fetchone_value(
            """
            WITH ins AS (
              INSERT INTO finance_transactions(tenant_id, ts, amount, currency, category, merchant, note, external_id_or_hash, metadata)
              VALUES (%(t)s, %(ts)s::timestamptz, %(amount)s, %(currency)s, %(category)s, %(merchant)s, %(note)s, %(h)s, '{}'::jsonb)
              ON CONFLICT (tenant_id, external_id_or_hash) DO NOTHING
              RETURNING id::text
            )
            SELECT id FROM ins
            UNION ALL
            SELECT id::text FROM finance_transactions WHERE tenant_id=%(t)s AND external_id_or_hash=%(h)s
            LIMIT 1;
            """,
            params={
                "t": tenant_id,
                "ts": payload["ts"],
                "amount": float(row["amount"]),
                "currency": currency,
                "category": payload.get("category"),
                "merchant": payload.get("merchant"),
                "note": payload.get("note"),
                "h": h,
            },
        )
        self.memory.db.execute(
            """
            INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload)
            VALUES (%(t)s, 'user', %(a)s, 'financelab.write_transaction', 'finance_tx', %(id)s,
                    jsonb_build_object('amount', %(amount)s, 'currency', %(currency)s, 'hash', %(h)s));
            """,
            params={"t": tenant_id, "a": actor_ref, "id": self._clean_id(tx_id), "amount": float(row["amount"]), "currency": currency, "h": h},
        )
        return {"status": "ok", "transaction_id": self._clean_id(tx_id)}
