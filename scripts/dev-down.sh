#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

docker compose down

echo "[dev-down] Services stopped."
