#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

STATE_FILE="runtime/RUNTIME_STATE.json"
SISTEMA_OUTBOX="runtime/outbox/sistema_snapshot.txt"
AGENT_FEED_OUTBOX="runtime/outbox/agent_feed_event.txt"

mkdir -p runtime/outbox

snapshot="$(scripts/publish_scope_a_snapshot.sh "$STATE_FILE")"
if [[ "$snapshot" != "NO_REPLY" ]]; then
  printf "%s\n" "$snapshot" > "$SISTEMA_OUTBOX"
else
  rm -f "$SISTEMA_OUTBOX"
fi

event_line="$(scripts/emit_scope_a_runtime_event.sh "$STATE_FILE")"
if [[ "$event_line" != "NO_EVENT" ]]; then
  printf "%s\n" "$event_line" > "$AGENT_FEED_OUTBOX"
else
  rm -f "$AGENT_FEED_OUTBOX"
fi

# stdout is useful for cron logs
if [[ "$snapshot" != "NO_REPLY" ]]; then
  echo "SISTEMA_READY"
else
  echo "SISTEMA_NO_REPLY"
fi

if [[ "$event_line" != "NO_EVENT" ]]; then
  echo "AGENT_FEED_READY"
else
  echo "AGENT_FEED_NO_EVENT"
fi
