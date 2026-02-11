#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/root/.openclaw/workspace}"
BRIDGE="$WORKSPACE/bridge"
REMOTE_DIR="$BRIDGE/remote"
INCOMING="$BRIDGE/incoming"
IMPORT_SH="$BRIDGE/import.sh"

mkdir -p "$INCOMING"

if [[ ! -d "$REMOTE_DIR/.git" ]]; then
  echo "ERROR: missing git checkout at $REMOTE_DIR"
  echo "Run: git clone git@github.com-ieltxu-tardis:ieltxu-tardis/openclaw-bridge.git $REMOTE_DIR"
  exit 1
fi

git -C "$REMOTE_DIR" pull --ff-only

if [[ ! -f "$REMOTE_DIR/outbox/latest-export.tgz" ]]; then
  echo "ERROR: no outbox/latest-export.tgz in remote repo"
  exit 1
fi

cp -f "$REMOTE_DIR/outbox/latest-export.tgz" "$INCOMING/latest-export.tgz"

bash "$IMPORT_SH"
