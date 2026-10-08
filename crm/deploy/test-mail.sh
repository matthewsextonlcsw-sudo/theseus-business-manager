#!/usr/bin/env bash
# End-to-end test of the email scripts against a real Stalwart, with a stand-in for Caddy that holds a
# throwaway certificate. Runs the real mail-setup.sh, mail-cert-sync.sh and backup.sh as root, the way
# the server does. Needs Linux, Docker with Compose, python3 and openssl; sends no mail outside the box.
#
#   sudo bash crm/deploy/test-mail.sh
set -euo pipefail
# Checks never use `grep -q` after a pipe: with pipefail, grep stopping early fails the writer (SIGPIPE).

here="$(cd "$(dirname "$0")" && pwd)"
[ "$(id -u)" = 0 ] || { echo "run as root: sudo bash $0" >&2; exit 2; }

host=mail.example.test
domain=example.test
stack="$(mktemp -d /tmp/mws-mail-test.XXXX)"
export COMPOSE_PROJECT_NAME="mwsmailtest$$"
export COMPOSE_FILE="docker-compose.yml:test.override.yml"
export MAIL_STACK_DIR="$stack"
pass=0 fail=0
check() { if eval "$2"; then echo "PASS  $1"; pass=$((pass + 1)); else echo "FAIL  $1"; fail=$((fail + 1)); fi; }
cleanup() { (cd "$stack" && docker compose --profile mail --profile mail-tools down -v >/dev/null 2>&1) || true; rm -rf "$stack"; }
trap '[ "${KEEP:-}" = 1 ] && echo "kept: $stack (project $COMPOSE_PROJECT_NAME)" || cleanup' EXIT

cp "$here"/docker-compose.yml "$here"/mail-setup.sh "$here"/mail-cert-sync.sh "$here"/backup.sh "$stack"/
mkdir -p "$stack/env" "$stack/crm" "$stack/fake-caddy"
for f in caddy twenty chatwoot connector; do : > "$stack/env/$f.env"; done
ln -s "$stack" "$stack/crm/deploy"   # backup.sh expects <stack>/crm/deploy

new_cert() {  # a throwaway certificate where Caddy keeps its own
  openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -days 2 -subj "/CN=$host" \
    -addext "subjectAltName=DNS:$host" -keyout "$stack/fake-caddy/$host.key" -out "$stack/fake-caddy/$host.crt" 2>/dev/null
  openssl x509 -in "$stack/fake-caddy/$host.crt" -noout -fingerprint -sha256 | cut -d= -f2
}
served() { echo | openssl s_client -connect "127.0.0.1:$1" -servername "$host" 2>/dev/null | openssl x509 -noout -fingerprint -sha256 | cut -d= -f2; }

cat > "$stack/test.override.yml" <<EOF
services:
  caddy:
    image: busybox:1.37
    command: ["sleep", "86400"]
    env_file: !reset []
    ports: !reset []
    volumes: !override
      - ./fake-caddy:/data/caddy/certificates/acme-v02.api.letsencrypt.org-directory/$host:ro
  stalwart:
    ports: !override
      - "127.0.0.1:21025:25"
      - "127.0.0.1:21465:465"
      - "127.0.0.1:21993:993"
EOF

cd "$stack"
docker compose up -d caddy >/dev/null

echo "== 1. certificate copy, before the mail server exists"
# shellcheck disable=SC2034  # used inside check strings
first_fp="$(new_cert)"
./mail-cert-sync.sh "$host"
check "copied certificate is owned by Stalwart's user, key private" \
  '[ "$(stat -c %u:%a mail-certs/mail.key)" = 2000:600 ] && [ "$(stat -c %u:%a mail-certs)" = 2000:700 ]'

echo "== 2. first setup"
./mail-setup.sh "$host" "$domain" matthew hello postmaster | tee setup1.log
check "mailbox credentials written for the owner, root-only" '[ "$(stat -c %a env/mail-new-credentials.txt)" = 600 ] && grep -q "matthew@$domain" env/mail-new-credentials.txt'
check "one-time setup login retired" '! grep -q STALWART_RECOVERY_ADMIN env/mail.env'
check "no password printed during setup" '! grep -qiE "password: *[0-9a-f]{20}" setup1.log'
check "DNS records listed: MX, SPF, two DKIM keys" 'grep -q " MX " setup1.log && grep -q "v=spf1 mx -all" setup1.log && [ "$(grep -c "_domainkey" setup1.log)" = 2 ]'
check "mail ports present the certificate from Caddy" '[ "$(served 21993)" = "$first_fp" ] && [ "$(served 21465)" = "$first_fp" ]'

echo "== 3. second run changes nothing"
# shellcheck disable=SC2034
before="$(sha256sum env/mail-new-credentials.txt env/mail-admin.pw)"
./mail-setup.sh "$host" "$domain" matthew hello postmaster > setup2.log
check "mailbox and admin passwords unchanged on a re-run" '[ "$before" = "$(sha256sum env/mail-new-credentials.txt env/mail-admin.pw)" ]'

echo "== 4. mail flows"
pw="$(sed -n 's/^Password: *//p' env/mail-new-credentials.txt)"
check "mail in, mail out, alias and DKIM" "python3 -I - '$pw' '$domain' <<'PY'
import imaplib, smtplib, ssl, sys, time
from email.message import EmailMessage
pw, domain = sys.argv[1], sys.argv[2]
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
m = EmailMessage(); m['From'] = 'someone@gmail.com'; m['To'] = 'hello@' + domain; m['Subject'] = 'inbound'; m.set_content('hi')
with smtplib.SMTP('127.0.0.1', 21025, timeout=20) as s:
    s.ehlo('outside.test'); s.starttls(context=ctx); s.ehlo('outside.test'); s.send_message(m)
m = EmailMessage(); m['From'] = 'matthew@' + domain; m['To'] = 'postmaster@' + domain; m['Subject'] = 'outbound'; m.set_content('hi')
with smtplib.SMTP_SSL('127.0.0.1', 21465, context=ctx, timeout=20) as s:
    s.login('matthew@' + domain, pw); s.send_message(m)
time.sleep(4)
found = {}
with imaplib.IMAP4_SSL('127.0.0.1', 21993, ssl_context=ctx, timeout=20) as i:
    i.login('matthew@' + domain, pw)
    for box in ('INBOX', '\"Junk Mail\"'):
        i.select(box, readonly=True)
        for n in i.search(None, 'ALL')[1][0].split():
            h = i.fetch(n, '(BODY.PEEK[HEADER.FIELDS (SUBJECT DKIM-SIGNATURE)])')[1][0][1].decode().lower()
            found['inbound' if 'inbound' in h else 'outbound'] = 'dkim-signature' in h
sys.exit(0 if 'inbound' in found and found.get('outbound') else 1)
PY"
unset pw

echo "== 5. certificate renewal"
# shellcheck disable=SC2034
second_fp="$(new_cert)"
./mail-cert-sync.sh "$host" | tee sync.log
sleep 6
check "renewed certificate copied and served after the restart" 'grep -q restarted sync.log && [ "$(served 21993)" = "$second_fp" ]'
check "an unchanged certificate does not restart the mail server" './mail-cert-sync.sh "$host" | grep unchanged >/dev/null'

echo "== 6. backup"
bash backup.sh "$stack" mail >/dev/null
check "mailbox backup written and readable" 'tar tzf backups/mail-*.tgz | grep "var/lib/stalwart/" >/dev/null'
check "mail server running again after the backup" '[ -n "$(docker compose --profile mail ps -q stalwart)" ]'

echo
echo "$pass passed, $fail failed"
[ "$fail" = 0 ]
