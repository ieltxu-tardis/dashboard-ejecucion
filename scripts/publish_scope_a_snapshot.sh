#!/usr/bin/env bash
set -euo pipefail

STATE_FILE="${1:-runtime/RUNTIME_STATE.json}"

if [[ ! -f "$STATE_FILE" ]]; then
  echo "NO_REPLY"
  exit 0
fi

python3 - "$STATE_FILE" <<'PY'
import json
import sys
from pathlib import Path

state_path = Path(sys.argv[1])

try:
    data = json.loads(state_path.read_text(encoding="utf-8"))
except Exception:
    print("NO_REPLY")
    sys.exit(0)

marker = data.get("material_change_marker")
if not marker:
    print("NO_REPLY")
    sys.exit(0)

def line_for(item, section):
    if not isinstance(item, dict):
        return f"- {item}"

    if section == "ACTIVE_NOW":
        ident = item.get("id", "?")
        owner = item.get("owner", "?")
        task = item.get("task", "(no task)")
        return f"- [{ident}] {owner}: {task}"

    if section == "BLOCKED":
        ident = item.get("id", "?")
        owner = item.get("owner", "?")
        blocked_by = item.get("blocked_by", "(no blocker)")
        return f"- [{ident}] {owner}: {blocked_by}"

    if section == "DONE":
        ident = item.get("id", "?")
        owner = item.get("owner", "?")
        result = item.get("result", "(no result)")
        return f"- [{ident}] {owner}: {result}"

    # NEXT_TRIGGER
    ident = item.get("id", "?")
    owner = item.get("owner", "?")
    action = item.get("next_action", item.get("trigger_condition", "(no trigger)"))
    return f"- [{ident}] {owner}: {action}"


def render(section):
    val = data.get(section, [])
    print(f"{section}:")
    if isinstance(val, list) and val:
        for i in val[:3]:
            print(line_for(i, section))
        if len(val) > 3:
            print(f"- ... (+{len(val)-3} more)")
    else:
        print("- none")

print(f"SCOPE_A_SNAPSHOT marker={marker}")
for sec in ["ACTIVE_NOW", "BLOCKED", "DONE", "NEXT_TRIGGER"]:
    render(sec)
PY
