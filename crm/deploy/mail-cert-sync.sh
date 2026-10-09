#!/usr/bin/env bash
# Copy Caddy's TLS certificate for the mail host to the mail server, and restart the mail server only
# when the certificate changed (Stalwart reads certificate files when it starts). Stalwart's own docs
# describe this copy for servers behind Caddy. Run nightly by mws-mail-certs.timer and once by
# deploy.sh mail, as root, from the stack folder:
#
#   mail-cert-sync.sh <mail host>
set -euo pipefail

host="${1:?usage: mail-cert-sync.sh <mail host>}"
[[ $host =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$ ]] || { echo "bad mail host: $host" >&2; exit 2; }
cd "${MAIL_STACK_DIR:-$(dirname "$0")}"

dc() { docker compose --profile mail "$@"; }

# Caddy keeps one folder per issuer (Let's Encrypt, or ZeroSSL as its fallback): take the newest.
src="$(dc exec -T caddy sh -c "ls -td /data/caddy/certificates/*/$host 2>/dev/null | head -n 1")"
[ -n "$src" ] || { echo "Caddy has no certificate for $host yet. Is its DNS record in place?" >&2; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
dc exec -T caddy cat "$src/$host.crt" > "$tmp/mail.crt"
dc exec -T caddy cat "$src/$host.key" > "$tmp/mail.key"

openssl x509 -in "$tmp/mail.crt" -noout -checkend 3600 >/dev/null \
  || { echo "Caddy's certificate for $host is expired or unreadable; nothing copied." >&2; exit 1; }
[ "$(openssl x509 -in "$tmp/mail.crt" -noout -pubkey)" = "$(openssl pkey -in "$tmp/mail.key" -pubout)" ] \
  || { echo "Caddy's certificate and key for $host don't match; nothing copied." >&2; exit 1; }

mkdir -p mail-certs
if cmp -s "$tmp/mail.crt" mail-certs/mail.crt && cmp -s "$tmp/mail.key" mail-certs/mail.key; then
  echo "Mail certificate unchanged (valid until $(openssl x509 -in mail-certs/mail.crt -noout -enddate | cut -d= -f2))."
  exit 0
fi

# Stalwart runs as user 2000 and reads the files through a read-only mount. The owner is set with chown:
# the uutils `install` on Ubuntu 26.04 rejects a numeric -o for a user this host doesn't have.
install -m 644 "$tmp/mail.crt" mail-certs/mail.crt
install -m 600 "$tmp/mail.key" mail-certs/mail.key
chown 2000:2000 mail-certs/mail.crt mail-certs/mail.key mail-certs
chmod 700 mail-certs

if [ -n "$(dc ps -q stalwart)" ]; then
  dc restart stalwart >/dev/null
  echo "Mail certificate updated; mail server restarted."
else
  echo "Mail certificate copied."
fi
