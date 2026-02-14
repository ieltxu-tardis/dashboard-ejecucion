#!/usr/bin/env bash
set -euo pipefail

STATE_FILE="${1:-runtime/RUNTIME_STATE.json}"
MARKER_CACHE_FILE="${2:-runtime/.scope_a_snapshot_marker}"

if [[ ! -f "$STATE_FILE" ]]; then
  echo "NO_REPLY"
  exit 0
fi

python3 - "$STATE_FILE" "$MARKER_CACHE_FILE" <<'PY'
import json
import sys
from pathlib import Path

state_path = Path(sys.argv[1])
marker_cache_path = Path(sys.argv[2])

try:
    data = json.loads(state_path.read_text(encoding="utf-8"))
except Exception:
    print("NO_REPLY")
    sys.exit(0)

marker = data.get("material_change_marker")
if not marker:
    print("NO_REPLY")
    sys.exit(0)

last_marker = ""
if marker_cache_path.exists():
    try:
        last_marker = marker_cache_path.read_text(encoding="utf-8").strip()
    except Exception:
        last_marker = ""

if marker == last_marker:
    print("NO_REPLY")
    sys.exit(0)

def compact(val, fallback="(none)"):
    if val is None:
        return fallback
    s = str(val).strip()
    return s if s else fallback


def section_lines(section_name, items):
    out = []
    if not isinstance(items, list) or not items:
        return ["- none"]

    for item in items[:3]:
        if not isinstance(item, dict):
            out.append(f"- {item}")
            continue

        ident = compact(item.get("id"), "?")
        owner = compact(item.get("owner"), "?")

        if section_name == "ACTIVE_NOW":
            task = compact(item.get("task"), "(no task)")
            out.append(f"- {ident} · {owner} — {task}")

        elif section_name == "BLOCKED":
            why = compact(item.get("blocked_by"), "(no blocker)")
            unblock = compact(item.get("unblock_action"), "(none)")
            out.append(f"- {ident} · {owner} — {why}")
            out.append(f"  ↳ Unblock: {unblock}")

        elif section_name == "DONE":
            result = compact(item.get("result"), "(no result)")
            evidence = compact(item.get("evidence"), "(none)")
            out.append(f"- {ident} · {owner} — {result}")
            out.append(f"  ↳ Evidence: {evidence}")

        else:  # NEXT_TRIGGER
            action = compact(item.get("next_action") or item.get("trigger_condition"), "(no trigger)")
            cond = compact(item.get("trigger_condition"), "(none)")
            out.append(f"- {ident} · {owner} — {action}")
            out.append(f"  ↳ Condition: {cond}")

    if len(items) > 3:
        out.append(f"- … (+{len(items)-3} more)")

    return out

updated = compact(data.get("generated_at"), "(unknown)")

print("## Scope A Runtime Snapshot")
print(f"Updated: {updated} · Marker: {marker}")
print()

print("### Active now")
for line in section_lines("ACTIVE_NOW", data.get("ACTIVE_NOW", [])):
    print(line)
print()

print("### Blocked")
for line in section_lines("BLOCKED", data.get("BLOCKED", [])):
    print(line)
print()

print("### Done")
for line in section_lines("DONE", data.get("DONE", [])):
    print(line)
print()

print("### Next trigger")
for line in section_lines("NEXT_TRIGGER", data.get("NEXT_TRIGGER", [])):
    print(line)

try:
    marker_cache_path.write_text(str(marker), encoding="utf-8")
except Exception:
    pass
PY
