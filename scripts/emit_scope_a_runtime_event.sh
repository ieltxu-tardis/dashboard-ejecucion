#!/usr/bin/env bash
set -euo pipefail

STATE_FILE="${1:-runtime/RUNTIME_STATE.json}"
CACHE_FILE="${2:-runtime/.scope_a_event_cache.json}"

if [[ ! -f "$STATE_FILE" ]]; then
  echo "NO_EVENT"
  exit 0
fi

python3 - "$STATE_FILE" "$CACHE_FILE" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

state_path = Path(sys.argv[1])
cache_path = Path(sys.argv[2])

def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def compact(v, fallback="(none)"):
    if v is None:
        return fallback
    s = str(v).strip()
    return s if s else fallback

try:
    current = json.loads(state_path.read_text(encoding="utf-8"))
except Exception:
    print("NO_EVENT")
    raise SystemExit(0)

if cache_path.exists():
    try:
        prev = json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception:
        prev = {}
else:
    prev = {}

def by_id(items):
    out = {}
    if isinstance(items, list):
        for i in items:
            if isinstance(i, dict):
                out[str(i.get("id", "?"))] = i
    return out

curr_active = by_id(current.get("ACTIVE_NOW", []))
prev_active = by_id(prev.get("ACTIVE_NOW", []))
curr_blocked = by_id(current.get("BLOCKED", []))
prev_blocked = by_id(prev.get("BLOCKED", []))
curr_done = by_id(current.get("DONE", []))
prev_done = by_id(prev.get("DONE", []))

# 1) COMPLETED
new_done_ids = [i for i in curr_done if i not in prev_done]
if new_done_ids:
    tid = max(new_done_ids, key=lambda x: str(curr_done.get(x, {}).get("completed_at", "")))
    item = curr_done[tid]
    payload = "\n".join([
        f"✅ COMPLETED · {tid}",
        f"Result: {compact(item.get('result'))}",
        f"Completed: {compact(item.get('completed_at'), now_iso())}",
        f"Evidence: {compact(item.get('evidence'))}",
    ])
    print(payload)
    cache_path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0)

# 2) BLOCKED
for tid, item in curr_blocked.items():
    p = prev_blocked.get(tid)
    if p is None or p.get("blocked_by") != item.get("blocked_by") or p.get("unblock_action") != item.get("unblock_action"):
        payload = "\n".join([
            f"⛔ BLOCKED · {tid}",
            f"Owner: {compact(item.get('owner'), '(unknown)')}",
            f"Why: {compact(item.get('blocked_by'), '(unknown)')}",
            f"Since: {compact(item.get('since'), now_iso())}",
            f"Unblock: {compact(item.get('unblock_action'))}",
        ])
        print(payload)
        cache_path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise SystemExit(0)

# 3) STARTED
new_active_ids = [i for i in curr_active if i not in prev_active]
if new_active_ids:
    tid = new_active_ids[0]
    item = curr_active[tid]
    payload = "\n".join([
        f"▶️ STARTED · {tid}",
        f"Owner: {compact(item.get('owner'), '(unknown)')}",
        f"Started: {compact(item.get('started_at'), now_iso())}",
        f"Evidence: {compact(item.get('evidence'))}",
    ])
    print(payload)
    cache_path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0)

# 4) HEARTBEAT
for tid, item in curr_active.items():
    p = prev_active.get(tid)
    if not p:
        continue
    changed_fields = []
    for k in ("task", "evidence", "progress", "progress_pct", "milestone", "resumed_at"):
        if p.get(k) != item.get(k) and item.get(k) is not None:
            changed_fields.append(k)
    if changed_fields:
        payload = "\n".join([
            f"💓 HEARTBEAT · {tid}",
            f"Progress: {', '.join(changed_fields)}",
            f"Evidence: {compact(item.get('evidence'))}",
            f"Time: {now_iso()}",
        ])
        print(payload)
        cache_path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise SystemExit(0)

print("NO_EVENT")
cache_path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
