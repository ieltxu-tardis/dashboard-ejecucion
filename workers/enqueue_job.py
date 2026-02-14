#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from memory_service.db import PostgresExec
from memory_service.jobs import JobQueueService
from memory_service.service import PostgresMemoryService, get_default_tenant_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant-id", default="default")
    parser.add_argument("--type", required=True, choices=["embed_document", "summarize_period", "memory_compact"])
    parser.add_argument("--doc-id")
    parser.add_argument("--period", default="weekly")
    parser.add_argument("--scope", default=None)
    args = parser.parse_args()

    db = PostgresExec(repo_root=str(Path(__file__).resolve().parents[1]))
    svc = PostgresMemoryService.build()

    tenant_id = args.tenant_id
    if tenant_id == "default":
        tenant_id = get_default_tenant_id(svc)

    q = JobQueueService(db)
    if args.type == "embed_document":
        if not args.doc_id:
            raise SystemExit("--doc-id is required for embed_document")
        out = q.enqueue_embedding_job(tenant_id=tenant_id, doc_id=args.doc_id)
    elif args.type == "summarize_period":
        out = q.enqueue_summary_job(tenant_id=tenant_id, period=args.period, scope=args.scope)
    else:
        out = q.enqueue_job(
            tenant_id=tenant_id,
            job_type="memory_compact",
            payload={"scope": args.scope},
            dedupe_key=f"compact:{tenant_id}:{args.scope or 'all'}",
        )

    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
