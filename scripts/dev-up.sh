#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
  echo "[dev-up] .env not found. Copy .env.example to .env and set real secrets first."
  exit 1
fi

docker compose up -d

echo "[dev-up] Services starting..."
docker compose ps
