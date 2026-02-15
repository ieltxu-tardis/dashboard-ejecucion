#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/dev-up.sh
./scripts/db-migrate.sh
./scripts/db-seed.sh

# Run worker on host (phase 4 baseline) so it can use docker compose exec bridge
WORKER_LOG=/tmp/openclaw-worker.log
# Clean any stale running jobs from interrupted local tests
PYTHONPATH=. python3 - <<'PY'
from memory_service.db import PostgresExec
PostgresExec().execute("UPDATE jobs SET status='failed', last_error='stale_running_reset_by_test' WHERE status='running';")
PY

PYTHONPATH=. python3 workers/jobs_worker.py > "$WORKER_LOG" 2>&1 &
WORKER_PID=$!
cleanup() {
  kill "$WORKER_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

PYTHONPATH=. python3 -m unittest tests/test_jobs_unit.py

# Create document (this should enqueue embed job)
DOC_OUT=$(PYTHONPATH=. python3 - <<'PY'
import hashlib, json, time
from memory_service.service import PostgresMemoryService, get_default_tenant_id
svc = PostgresMemoryService.build()
tenant_id = get_default_tenant_id(svc)
content = f"Phase4 jobs embedding smoke document {time.time()}"
out = svc.write_document({
    "tenant_id": tenant_id,
    "actor_ref": "jobs-test",
    "intent_type": "explicit_user_intent",
    "reason": "jobs smoke",
    "source": "test-jobs",
    "scope": "memory:write",
    "confidence": 0.95,
    "source_type": "smoke",
    "source_ref": "jobs-smoke",
    "content": content,
    "content_hash": hashlib.sha256(content.encode()).hexdigest(),
    "metadata": {"phase": 4}
})
print(json.dumps({"tenant_id": tenant_id, "doc_id": str(out["id"]).splitlines()[0]}))
PY
)

TENANT_ID=$(echo "$DOC_OUT" | python3 -c 'import sys,json; lines=[l for l in sys.stdin.read().splitlines() if l.strip()]; obj=json.loads(lines[-1]); print(obj["tenant_id"])')
DOC_ID=$(echo "$DOC_OUT" | python3 -c 'import sys,json; lines=[l for l in sys.stdin.read().splitlines() if l.strip()]; obj=json.loads(lines[-1]); print(obj["doc_id"])')

# Enqueue explicit embed job (do not rely on implicit enqueue path)
PYTHONPATH=. python3 - <<PY
from memory_service.db import PostgresExec
from memory_service.jobs import JobQueueService
q = JobQueueService(PostgresExec())
out = q.enqueue_embedding_job(tenant_id="$TENANT_ID", doc_id="$DOC_ID")
print(out)
PY

# wait for embedding rows
for i in $(seq 1 30); do
  CNT=$(PYTHONPATH=. python3 - <<PY
from memory_service.db import PostgresExec
db = PostgresExec()
cnt = db.fetchone_value("SELECT COUNT(*)::text FROM embeddings WHERE tenant_id=%(tenant_id)s AND doc_id=%(doc_id)s::uuid;", params={"tenant_id":"$TENANT_ID","doc_id":"$DOC_ID"})
print(cnt or "0")
PY
)
  if [[ "$CNT" =~ ^[0-9]+$ ]] && [[ "$CNT" -gt 0 ]]; then
    break
  fi
  sleep 2
done

if [[ ! "$CNT" =~ ^[0-9]+$ ]] || [[ "$CNT" -le 0 ]]; then
  echo "test-jobs: FAIL embeddings not generated"
  exit 1
fi

# semantic search smoke
SEM=$(PYTHONPATH=. python3 - <<PY
from memory_service.embedding_provider import LocalHashEmbeddingProvider
from memory_service.service import PostgresMemoryService
provider = LocalHashEmbeddingProvider()
svc = PostgresMemoryService.build()
q = provider.embed_text("Phase4 jobs embedding smoke document")
res = svc.semantic_search("$TENANT_ID", q, top_k=3)
print(len(res))
PY
)
SEM_NUM=$(echo "$SEM" | python3 -c 'import sys; lines=[l for l in sys.stdin.read().splitlines() if l.strip()]; print(lines[-1])')
if [[ "$SEM_NUM" -lt 1 ]]; then
  echo "test-jobs: FAIL semantic search empty"
  exit 1
fi

echo "test-jobs: SUCCESS (embeddings=$CNT, semantic_hits=$SEM_NUM)"
