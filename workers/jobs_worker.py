#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from memory_service.chunking import chunk_text
from memory_service.db import PostgresExec
from memory_service.embedding_provider import LocalHashEmbeddingProvider
from memory_service.jobs import compute_backoff_seconds, should_retry

POLL_SECONDS = float(os.getenv("JOB_POLL_SECONDS", "1.5"))
MAX_RETRY = int(os.getenv("JOB_MAX_RETRY", "5"))
BACKOFF_BASE_SECONDS = float(os.getenv("JOB_BACKOFF_BASE_SECONDS", "2"))
CHUNK_BUDGET = int(os.getenv("JOB_MAX_CHUNKS_PER_DOC", "128"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str, **k) -> None:
    payload = {"ts": utc_now(), "msg": msg, **k}
    print(json.dumps(payload, ensure_ascii=False), flush=True)


def record_run(db: PostgresExec, tenant_id: str, job_type: str, status: str, error_message: str | None = None):
    db.execute(
        """
        INSERT INTO job_runs(tenant_id, job_type, status, attempts, started_at, ended_at, error_message, metadata)
        VALUES (%(tenant_id)s, %(job_type)s, %(status)s, 1, NOW(), NOW(), %(error_message)s, '{}'::jsonb);
        """,
        params={
            "tenant_id": tenant_id,
            "job_type": job_type,
            "status": status,
            "error_message": error_message,
        },
    )


def process_embed_document(db: PostgresExec, tenant_id: str, job_id: str, payload: dict):
    doc_id = payload.get("doc_id")
    model = payload.get("model", "local-hash-1536")
    if not doc_id:
        raise ValueError("missing_doc_id")

    row = db.fetchall_json(
        "SELECT id::text, content FROM documents WHERE tenant_id = %(tenant_id)s AND id = %(doc_id)s::uuid LIMIT 1",
        params={"tenant_id": tenant_id, "doc_id": doc_id},
    )
    if not row:
        raise ValueError("document_not_found")

    content = row[0]["content"]
    chunks = chunk_text(content)
    if len(chunks) > CHUNK_BUDGET:
        chunks = chunks[:CHUNK_BUDGET]

    provider = LocalHashEmbeddingProvider(dimension=1536, model_name=model)

    for idx, chunk in enumerate(chunks):
        chunk_id = f"c{idx:04d}"
        token_estimate = max(1, len(chunk) // 4)

        db.execute(
            """
            INSERT INTO document_chunks(tenant_id, doc_id, chunk_id, chunk_text, chunk_index, token_estimate, metadata)
            VALUES (%(tenant_id)s, %(doc_id)s::uuid, %(chunk_id)s, %(chunk_text)s, %(chunk_index)s, %(token_estimate)s, '{}'::jsonb)
            ON CONFLICT (tenant_id, doc_id, chunk_id)
            DO UPDATE SET chunk_text = EXCLUDED.chunk_text, token_estimate = EXCLUDED.token_estimate;
            """,
            params={
                "tenant_id": tenant_id,
                "doc_id": doc_id,
                "chunk_id": chunk_id,
                "chunk_text": chunk,
                "chunk_index": idx,
                "token_estimate": token_estimate,
            },
        )

        vec = provider.embed_text(chunk)
        vec_str = "[" + ",".join(str(float(v)) for v in vec) + "]"

        db.execute(
            """
            INSERT INTO embeddings(tenant_id, doc_id, chunk_id, embedding, model, metadata)
            VALUES (%(tenant_id)s, %(doc_id)s::uuid, %(chunk_id)s, %(embedding)s::vector, %(model)s, '{}'::jsonb)
            ON CONFLICT (tenant_id, doc_id, chunk_id, model)
            DO UPDATE SET embedding = EXCLUDED.embedding;
            """,
            params={
                "tenant_id": tenant_id,
                "doc_id": doc_id,
                "chunk_id": chunk_id,
                "embedding": vec_str,
                "model": model,
            },
        )


def process_summarize_period(db: PostgresExec, tenant_id: str, job_id: str, payload: dict):
    period = payload.get("period", "weekly")
    scope = payload.get("scope")
    docs = db.fetchall_json(
        "SELECT id::text, source_ref, left(content, 120) as snippet, created_at FROM documents WHERE tenant_id = %(tenant_id)s ORDER BY created_at DESC LIMIT 10",
        params={"tenant_id": tenant_id},
    )

    lines = [f"Summary period={period} scope={scope or 'all'}"]
    for d in docs[:5]:
        lines.append(f"- {d.get('source_ref') or 'doc'} :: {d.get('snippet')}")
    summary = "\n".join(lines)

    from hashlib import sha256

    content_hash = sha256(summary.encode("utf-8")).hexdigest()
    db.execute(
        """
        INSERT INTO documents(tenant_id, source_type, source_ref, content, content_hash, metadata)
        VALUES (%(tenant_id)s, 'summary', %(source_ref)s, %(content)s, %(content_hash)s,
                jsonb_build_object('generated_by','system','job_id',%(job_id)s))
        ON CONFLICT (tenant_id, content_hash) DO NOTHING;
        """,
        params={
            "tenant_id": tenant_id,
            "source_ref": f"summary:{period}:{scope or 'all'}",
            "content": summary,
            "content_hash": content_hash,
            "job_id": job_id,
        },
    )

    db.execute(
        """
        INSERT INTO audit_log(tenant_id, actor_type, actor_ref, action, target_type, target_ref, payload)
        VALUES (%(tenant_id)s, 'system', 'worker', 'summarize_period', 'document', %(job_id)s,
                jsonb_build_object('period', %(period)s, 'scope', %(scope)s));
        """,
        params={"tenant_id": tenant_id, "job_id": job_id, "period": period, "scope": scope},
    )


def fetch_next_job(db: PostgresExec) -> dict | None:
    job_id = db.fetchone_value(
        """
        SELECT id::text
        FROM jobs
        WHERE status = 'queued'
          AND scheduled_at <= NOW()
        ORDER BY priority ASC, created_at ASC
        LIMIT 1;
        """
    )
    if not job_id:
        return None

    db.execute(
        "UPDATE jobs SET status='running', updated_at=NOW() WHERE id = %(job_id)s::uuid AND status='queued';",
        params={"job_id": job_id},
    )

    rows = db.fetchall_json(
        """
        SELECT id::text, tenant_id::text, type, payload, status, attempts, max_attempts
        FROM jobs
        WHERE id = %(job_id)s::uuid AND status='running'
        LIMIT 1;
        """,
        params={"job_id": job_id},
    )
    return rows[0] if rows else None


def fail_job(db: PostgresExec, job: dict, err: str, duration_ms: int):
    attempts = int(job["attempts"]) + 1
    max_attempts = int(job.get("max_attempts") or MAX_RETRY)
    status = "failed" if not should_retry(attempts, max_attempts) else "queued"
    backoff = compute_backoff_seconds(attempts, BACKOFF_BASE_SECONDS) if status == "queued" else 0
    db.execute(
        """
        UPDATE jobs
        SET status = %(status)s,
            attempts = %(attempts)s,
            last_error = %(last_error)s,
            scheduled_at = CASE WHEN %(status)s = 'queued' THEN NOW() + (%(backoff)s || ' seconds')::interval ELSE scheduled_at END,
            updated_at = NOW()
        WHERE id = %(job_id)s::uuid;
        """,
        params={
            "status": status,
            "attempts": attempts,
            "last_error": err[:500],
            "backoff": backoff,
            "job_id": job["id"],
        },
    )
    record_run(db, job["tenant_id"], job["type"], status, err[:500])
    db.execute(
        """
        INSERT INTO observability_events(tenant_id, component, route, event_type, outcome, job_type, error_code, latency_ms)
        VALUES (%(tenant_id)s, 'worker', 'job_process', 'job_process', 'error', %(job_type)s, %(error_code)s, %(latency_ms)s);
        """,
        params={
            "tenant_id": job["tenant_id"],
            "job_type": job["type"],
            "error_code": err[:120],
            "latency_ms": duration_ms,
        },
    )


def complete_job(db: PostgresExec, job: dict, duration_ms: int):
    db.execute("UPDATE jobs SET status='done', updated_at=NOW() WHERE id = %(job_id)s::uuid;", params={"job_id": job["id"]})
    record_run(db, job["tenant_id"], job["type"], "done", None)
    db.execute(
        """
        INSERT INTO observability_events(tenant_id, component, route, event_type, outcome, job_type, latency_ms)
        VALUES (%(tenant_id)s, 'worker', 'job_process', 'job_process', 'ok', %(job_type)s, %(latency_ms)s);
        """,
        params={"tenant_id": job["tenant_id"], "job_type": job["type"], "latency_ms": duration_ms},
    )


def process_job(db: PostgresExec, job: dict):
    if job["type"] == "embed_document":
        process_embed_document(db, job["tenant_id"], job["id"], job["payload"])
    elif job["type"] == "summarize_period":
        process_summarize_period(db, job["tenant_id"], job["id"], job["payload"])
    elif job["type"] == "memory_compact":
        pass
    else:
        raise ValueError(f"unknown_job_type:{job['type']}")


def main() -> int:
    db = PostgresExec(repo_root=str(Path(__file__).resolve().parents[1]))
    log("worker_started", mode="db_poll")
    while True:
        job = fetch_next_job(db)
        if not job:
            time.sleep(POLL_SECONDS)
            continue
        started = time.time()
        try:
            process_job(db, job)
            duration_ms = int((time.time() - started) * 1000)
            complete_job(db, job, duration_ms)
            log("job_done", job_id=job["id"], job_type=job["type"], tenant_id=job["tenant_id"], latency_ms=duration_ms)
        except Exception as e:
            duration_ms = int((time.time() - started) * 1000)
            err = f"{type(e).__name__}:{e}"
            fail_job(db, job, err, duration_ms)
            log("job_failed", job_id=job["id"], error=err, latency_ms=duration_ms)
            traceback.print_exc()


if __name__ == "__main__":
    raise SystemExit(main())
