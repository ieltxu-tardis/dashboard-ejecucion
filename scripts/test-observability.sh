#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/dev-up.sh
./scripts/db-migrate.sh
./scripts/db-seed.sh

# Start worker and metrics server on host
WORKER_LOG=/tmp/openclaw-worker-obsv.log
METRICS_LOG=/tmp/openclaw-metrics.log
PYTHONPATH=. python3 workers/jobs_worker.py > "$WORKER_LOG" 2>&1 &
WPID=$!
PYTHONPATH=. python3 observability/metrics_server.py > "$METRICS_LOG" 2>&1 &
MPID=$!
cleanup() {
  kill "$WPID" >/dev/null 2>&1 || true
  kill "$MPID" >/dev/null 2>&1 || true
}
trap cleanup EXIT
sleep 2

# Generate activity: write doc -> enqueue embed -> semantic search
PYTHONPATH=. python3 - <<'PY'
import hashlib,time
from memory_service.db import PostgresExec
from memory_service.jobs import JobQueueService
from memory_service.service import PostgresMemoryService,get_default_tenant_id
from memory_service.embedding_provider import LocalHashEmbeddingProvider

svc=PostgresMemoryService.build()
tid=get_default_tenant_id(svc)
content=f"observability smoke {time.time()}"
out=svc.write_document({
  "tenant_id":tid,
  "actor_ref":"obs-test",
  "intent_type":"explicit_user_intent",
  "reason":"obs smoke",
  "source":"test-observability",
  "scope":"memory:write",
  "confidence":0.95,
  "source_type":"smoke",
  "source_ref":"obs-smoke",
  "content":content,
  "content_hash":hashlib.sha256(content.encode()).hexdigest(),
  "metadata":{"obs":True}
})
q=JobQueueService(PostgresExec())
q.enqueue_embedding_job(tenant_id=tid, doc_id=out["id"])
# wait embeddings
for _ in range(40):
  c=PostgresExec().fetchone_value("SELECT COUNT(*)::text FROM embeddings WHERE tenant_id=%(t)s AND doc_id=%(d)s::uuid",params={"t":tid,"d":out["id"]})
  if int(c or '0')>0:
    break
  time.sleep(1)
prov=LocalHashEmbeddingProvider()
svc.semantic_search(tid, prov.embed_text(content), top_k=3)
PY

METRICS=$(curl -fsS http://127.0.0.1:9464/metrics)

for m in \
  openclaw_requests_total \
  openclaw_errors_total \
  openclaw_jobs_enqueued_total \
  openclaw_jobs_processed_total \
  openclaw_queue_depth \
  openclaw_embeddings_generated_total \
  openclaw_semantic_search_queries_total \
  openclaw_semantic_search_hits_total; do
  echo "$METRICS" | grep -q "$m" || { echo "missing metric: $m"; exit 1; }
done

echo "test-observability: SUCCESS"
