from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .db import PostgresExec


@dataclass
class QueueConfig:
    stream_name: str = "jobs:stream"
    max_jobs_per_request: int = 10


def compute_backoff_seconds(attempt: int, base: float = 2.0) -> float:
    return float(base) * (2 ** max(0, attempt - 1))


def should_retry(attempts: int, max_attempts: int) -> bool:
    return attempts < max_attempts


class JobQueueService:
    def __init__(self, db: PostgresExec, config: QueueConfig | None = None):
        self.db = db
        self.config = config or QueueConfig()

    def enqueue_job(
        self,
        *,
        tenant_id: str,
        job_type: str,
        payload: dict[str, Any],
        dedupe_key: str,
        priority: int = 5,
        timeout_seconds: int = 120,
        max_attempts: int = 5,
    ) -> dict[str, Any]:
        existing = self.db.fetchone_value(
            """
            SELECT id::text FROM jobs
            WHERE tenant_id = %(tenant_id)s
              AND dedupe_key = %(dedupe_key)s
              AND status IN ('queued','running','done')
            LIMIT 1;
            """,
            params={"tenant_id": tenant_id, "dedupe_key": dedupe_key},
        )
        if existing:
            return {"job_id": existing, "deduped": True}

        count_q = self.db.fetchone_value(
            "SELECT COUNT(*)::text FROM jobs WHERE tenant_id = %(tenant_id)s AND status = 'queued';",
            params={"tenant_id": tenant_id},
        )
        if int(count_q or "0") >= self.config.max_jobs_per_request:
            self.db.execute(
                """
                INSERT INTO observability_events(tenant_id, component, route, event_type, outcome, error_code)
                VALUES (%(tenant_id)s, 'queue', 'enqueue', 'policy_denied', 'error', 'queue_budget_exceeded');
                """,
                params={"tenant_id": tenant_id},
            )
            raise ValueError("enqueue_denied:queue_budget_exceeded")

        job_id = self.db.fetchone_value(
            """
            INSERT INTO jobs(tenant_id, type, payload, status, priority, dedupe_key, timeout_seconds, max_attempts)
            VALUES (%(tenant_id)s, %(job_type)s, %(payload)s::jsonb, 'queued', %(priority)s, %(dedupe_key)s, %(timeout_seconds)s, %(max_attempts)s)
            RETURNING id::text;
            """,
            params={
                "tenant_id": tenant_id,
                "job_type": job_type,
                "payload": payload,
                "priority": int(priority),
                "dedupe_key": dedupe_key,
                "timeout_seconds": int(timeout_seconds),
                "max_attempts": int(max_attempts),
            },
        )
        if not job_id:
            raise RuntimeError("job_insert_failed")

        self.db.execute(
            """
            INSERT INTO observability_events(tenant_id, component, route, event_type, outcome, job_type)
            VALUES (%(tenant_id)s, 'queue', 'enqueue', 'job_enqueue', '2xx', %(job_type)s);
            """,
            params={"tenant_id": tenant_id, "job_type": job_type},
        )

        # Publish to Redis stream (best effort; DB remains source of truth)
        try:
            self.db.run_redis_cli([
                "XADD",
                self.config.stream_name,
                "*",
                "job_id",
                job_id,
                "tenant_id",
                tenant_id,
                "type",
                job_type,
                "payload",
                json.dumps(payload),
            ])
        except Exception:
            pass

        return {"job_id": job_id, "deduped": False}

    def enqueue_embedding_job(self, tenant_id: str, doc_id: str, model: str = "local-hash-1536") -> dict[str, Any]:
        dedupe_key = f"embed:{tenant_id}:{doc_id}:{model}"
        return self.enqueue_job(
            tenant_id=tenant_id,
            job_type="embed_document",
            payload={"doc_id": doc_id, "model": model},
            dedupe_key=dedupe_key,
            priority=5,
            timeout_seconds=120,
            max_attempts=5,
        )

    def enqueue_summary_job(self, tenant_id: str, period: str, scope: str | None = None) -> dict[str, Any]:
        dedupe_key = f"summary:{tenant_id}:{period}:{scope or 'all'}"
        return self.enqueue_job(
            tenant_id=tenant_id,
            job_type="summarize_period",
            payload={"period": period, "scope": scope},
            dedupe_key=dedupe_key,
            priority=6,
            timeout_seconds=180,
            max_attempts=3,
        )
