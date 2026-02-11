#!/usr/bin/env bash
set -euo pipefail

# OpenClaw side: import sanitized bridge exports into workspace sandbox
WORKSPACE="${WORKSPACE:-/root/.openclaw/workspace}"
BRIDGE_DIR="$WORKSPACE/bridge"
INCOMING="$BRIDGE_DIR/incoming"
IMPORTS="$BRIDGE_DIR/imports"
SANDBOX="$BRIDGE_DIR/sandbox"
LOGS="$BRIDGE_DIR/logs"
STATE="$BRIDGE_DIR/state"

mkdir -p "$INCOMING" "$IMPORTS" "$SANDBOX" "$LOGS" "$STATE"

ARCHIVE="${1:-}"
if [[ -z "$ARCHIVE" ]]; then
  if [[ -f "$INCOMING/latest-export.tgz" ]]; then
    ARCHIVE="$INCOMING/latest-export.tgz"
  else
    ARCHIVE="$(ls -1t "$INCOMING"/*.tgz 2>/dev/null | head -n1 || true)"
  fi
fi

if [[ -z "$ARCHIVE" || ! -f "$ARCHIVE" ]]; then
  echo "ERROR: no .tgz archive found in $INCOMING"
  exit 1
fi

CURRENT_SHA="$(sha256sum "$ARCHIVE" | awk '{print $1}')"
LAST_SHA_FILE="$STATE/last_import.sha256"
if [[ -f "$LAST_SHA_FILE" ]]; then
  LAST_SHA="$(cat "$LAST_SHA_FILE")"
  if [[ "$CURRENT_SHA" == "$LAST_SHA" ]]; then
    echo "SKIP: archive unchanged ($ARCHIVE)"
    exit 0
  fi
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
RUN_DIR="$IMPORTS/import-$STAMP"
RUN_LOG="$LOGS/import-$STAMP.log"

mkdir -p "$RUN_DIR"

{
  echo "== Import run $STAMP =="
  echo "Archive: $ARCHIVE"

  tar -xzf "$ARCHIVE" -C "$RUN_DIR"

  # Clean macOS metadata noise.
  find "$RUN_DIR" -type f \( -name '._*' -o -name '.DS_Store' \) -delete || true

  # Keep only text-ish files in sandbox for now.
  SRC_ROOT="$(find "$RUN_DIR" -mindepth 1 -maxdepth 1 -type d | head -n1 || true)"
  if [[ -z "$SRC_ROOT" ]]; then
    echo "ERROR: archive has no top-level export directory"
    exit 1
  fi

  DEST="$SANDBOX/current"
  rm -rf "$DEST"
  mkdir -p "$DEST"

  rsync -a \
    --include='*/' \
    --include='*.md' --include='*.txt' --include='*.json' --include='*.yaml' --include='*.yml' \
    --exclude='*' \
    "$SRC_ROOT"/ "$DEST"/

  echo "Imported to: $DEST"
  echo "File count: $(find "$DEST" -type f | wc -l | tr -d ' ')"
  echo "Top files:"
  find "$DEST" -type f | sed "s|$DEST/||" | head -n 30

  ln -sfn "$RUN_DIR" "$IMPORTS/latest"
  echo "$CURRENT_SHA" > "$LAST_SHA_FILE"
  echo "SHA256: $CURRENT_SHA"
  echo "Log: $RUN_LOG"
} | tee "$RUN_LOG"
