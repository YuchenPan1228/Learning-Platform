#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! docker compose ps --status running | grep -q postgres; then
  echo "Postgres is not running. Start services with scripts/start-services.sh" >&2
  exit 1
fi

docker compose exec -T postgres psql -U quant_prep -d quant_prep -c \
  "SELECT cfgname FROM pg_ts_config WHERE cfgname = 'quant_prep_english';"

docker compose exec -T redis redis-cli ping

echo "PostgreSQL FTS config and Redis are available."
