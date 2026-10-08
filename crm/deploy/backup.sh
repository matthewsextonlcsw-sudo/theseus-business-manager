#!/usr/bin/env bash
# Database backups for the CRM stack (and the mailbox, when email is on), run nightly by mws-crm-backup.timer.
# Usage: backup.sh <stack folder> [mail]   e.g. backup.sh /opt/mws-crm   ("mail" = only the mailbox, now)
# Old backups are not deleted automatically; prune them by hand when you choose.
set -euo pipefail

dir="${1:?usage: backup.sh <stack folder> [mail]}"
only="${2:-}"
out="$dir/backups"
mkdir -p "$out"
chmod 700 "$out"
cd "$dir/crm/deploy"
stamp="$(date +%F-%H%M)"

if [ "$only" != mail ]; then
  # The stack's own Twenty only; an existing Twenty elsewhere is backed up where it runs.
  if [ -n "$(docker compose --profile twenty ps -q twenty-db 2>/dev/null)" ]; then
    docker compose --profile twenty exec -T twenty-db pg_dump -U postgres default | gzip > "$out/twenty-$stamp.sql.gz"
  fi
  docker compose exec -T chatwoot-db pg_dump -U postgres chatwoot | gzip > "$out/chatwoot-$stamp.sql.gz"
fi

# Email, when it is on: the mail server pauses for a few seconds so its database is copied whole.
# Mail that arrives meanwhile is refused for the moment and retried by the sender's server.
if [ -n "$(docker compose --profile mail ps -q stalwart 2>/dev/null)" ]; then
  docker compose --profile mail stop stalwart >/dev/null
  if ! docker compose --profile mail run --rm --no-deps -T --entrypoint tar stalwart \
      czf - /var/lib/stalwart /etc/stalwart 2>/dev/null > "$out/mail-$stamp.tgz"; then
    echo "mail backup FAILED" >&2
  fi
  docker compose --profile mail start stalwart >/dev/null
fi
echo "backups written: $(ls "$out"/*-"$stamp".* | tr '\n' ' ')"
