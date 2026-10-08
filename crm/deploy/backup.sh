#!/usr/bin/env bash
# Database backups for the CRM stack, run nightly by mws-crm-backup.timer.
# Usage: backup.sh <stack folder>   e.g. backup.sh /opt/mws-crm
# Old backups are not deleted automatically; prune them by hand when you choose.
set -euo pipefail

dir="${1:?usage: backup.sh <stack folder>}"
out="$dir/backups"
mkdir -p "$out"
chmod 700 "$out"
cd "$dir/crm/deploy"
stamp="$(date +%F-%H%M)"

docker compose exec -T twenty-db pg_dump -U postgres default | gzip > "$out/twenty-$stamp.sql.gz"
docker compose exec -T chatwoot-db pg_dump -U postgres chatwoot | gzip > "$out/chatwoot-$stamp.sql.gz"
echo "backups written: $out/*-$stamp.sql.gz"
