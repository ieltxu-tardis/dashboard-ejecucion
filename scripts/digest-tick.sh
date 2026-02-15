#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHONPATH=. python3 - <<'PY'
from memory_service.service import PostgresMemoryService, get_default_tenant_id
from modules.digesthub.service import DigestHubService
from pathlib import Path

repo=str(Path('.').resolve())
svc=PostgresMemoryService.build()
tenant=get_default_tenant_id(svc)
out=DigestHubService(repo, svc).tick_due(tenant_id=tenant)
print(out)
PY
