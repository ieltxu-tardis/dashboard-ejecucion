#!/usr/bin/env bash
set -euo pipefail

WS="/root/.openclaw/workspace"
REPO="$WS/.tmp-dashboard-pages"
URL="https://ieltxu-tardis.github.io/dashboard-ejecucion/"

# 1) repo sanity
[[ -f "$REPO/index.html" ]] || { echo "FAIL: missing $REPO/index.html"; exit 1; }
[[ -f "$REPO/data.json" ]] || { echo "FAIL: missing $REPO/data.json"; exit 1; }

# 2) no nested deploy path bug
if [[ -d "$REPO/dashboard" ]]; then
  echo "FAIL: nested /dashboard directory detected in deploy repo"
  exit 1
fi

# 3) timestamp freshness check from source data
updated_at=$(jq -r '.updatedAt // empty' "$WS/dashboard/data.json")
[[ -n "$updated_at" ]] || { echo "FAIL: dashboard/data.json missing updatedAt"; exit 1; }

# 4) site reachable
code=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
[[ "$code" == "200" ]] || { echo "FAIL: dashboard URL returned HTTP $code"; exit 1; }

echo "OK: healthcheck passed | updatedAt=$updated_at | http=$code"
