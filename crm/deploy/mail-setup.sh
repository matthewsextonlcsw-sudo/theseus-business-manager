#!/usr/bin/env bash
# Set up the Stalwart mail server, or bring its settings back in line on a later run.
# Runs on the server, as root, from the stack folder (deploy.sh mail calls it):
#
#   mail-setup.sh <mail host> <mail domain> <mailbox> [alias ...]
#   e.g. mail-setup.sh mail.example.com example.com matthew hello postmaster
#
# What it does, checked against Stalwart v0.16.25 with stalwart-cli 1.0.13:
#   1. First start only: Stalwart's setup wizard, as data. Hostname, domain, DKIM keys and console logs;
#      no ACME, because the TLS certificate is Caddy's (mail-cert-sync.sh copies it into mail-certs/).
#   2. Every run: one stable DKIM key (DNS is edited by hand, so keys must not rotate on their own) and the
#      visitor's real address from Caddy.
#   3. Once: the mailbox with its aliases, and the certificate, then the one-time setup login is retired,
#      as Stalwart's docs advise. The tools use the mail administrator's own login from then on.
#   4. Prints the DNS records the domain needs.
# Passwords are generated here and kept in env/ (root-only). They are never printed: a new mailbox's
# password is written to env/mail-new-credentials.txt for the owner to read once and delete.
set -euo pipefail

usage="usage: mail-setup.sh <mail host> <mail domain> <mailbox> [alias ...]"
host="${1:?$usage}"
domain="${2:?$usage}"
mailbox="${3:?$usage}"
shift 3
aliases=("$@")

name_re='^[a-z0-9]([a-z0-9._-]*[a-z0-9])?$'
host_re='^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$'
[[ $host =~ $host_re && $domain =~ $host_re ]] || { echo "mail host and domain must be lowercase DNS names" >&2; exit 2; }
for n in "$mailbox" "${aliases[@]}"; do
  [[ $n =~ $name_re ]] || { echo "mailbox and alias names must be lowercase letters, digits, dots, dashes" >&2; exit 2; }
done

cd "${MAIL_STACK_DIR:-$(dirname "$0")}"
umask 077
mkdir -p env

dc() { docker compose --profile mail --profile mail-tools "$@"; }
cli() { dc run --rm -T stalwart-cli --no-color "$@"; }
plan() { local out; out="$(cli apply --file /dev/stdin 2>&1)" || { printf '%s\n' "$out" >&2; return 1; }; }
secret() { openssl rand -hex 24; }
cli_login() { printf 'STALWART_URL=http://stalwart:8080\nSTALWART_USER=%s\nSTALWART_PASSWORD=%s\n' "$1" "$2" > env/mail-cli.env; }

# Ready = answers with our login. During first start only the Bootstrap object is reachable, and its
# "bootstrap mode" refusal also means the server is up.
wait_ready() {
  local out
  for _ in $(seq 1 45); do
    if out="$(cli query Domain 2>&1)" || grep -q "bootstrap mode" <<<"$out"; then return 0; fi
    sleep 2
  done
  echo "The mail server did not answer within 90 s. Look at: docker compose --profile mail logs stalwart" >&2
  exit 1
}

# One-time setup login (Stalwart's STALWART_RECOVERY_ADMIN) and the administrator's own password.
if [ ! -f env/mail.env ]; then
  setup_pw="$(secret)"
  printf 'STALWART_PUBLIC_URL=https://%s\nSTALWART_RECOVERY_ADMIN=admin:%s\n' "$host" "$setup_pw" > env/mail.env
  cli_login admin "$setup_pw"
  unset setup_pw
fi
[ -s env/mail-admin.pw ] || secret > env/mail-admin.pw
first_setup=0
grep -q '^STALWART_RECOVERY_ADMIN=' env/mail.env && first_setup=1

dc up -d stalwart
wait_ready

# 1. First start: the setup wizard's answers.
if ! dc exec -T stalwart test -f /etc/stalwart/config.json; then
  echo "First start: setting up $host for $domain"
  plan <<EOF
{"@type":"update","object":"Bootstrap","value":{"serverHostname":"$host","defaultDomain":"$domain","requestTlsCertificate":false,"generateDkimKeys":true,"tracer":{"@type":"Stdout","ansi":false,"enable":true,"level":"info"}}}
EOF
  dc restart stalwart
  wait_ready
fi

# 2. Every run: stable DKIM keys and the real visitor address. First setup also sets the admin password.
admin_pw="$(cat env/mail-admin.pw)"
{
  printf '%s\n' "{\"@type\":\"upsert\",\"object\":\"Domain\",\"matchOn\":[\"name\"],\"value\":{\"dom\":{\"name\":\"$domain\",\"dkimManagement\":{\"@type\":\"Manual\"}}}}"
  printf '%s\n' '{"@type":"update","object":"Http","value":{"useXForwarded":true}}'
  if [ "$first_setup" = 1 ]; then
    printf '%s\n' "{\"@type\":\"upsert\",\"object\":\"Account\",\"matchOn\":[\"name\"],\"value\":{\"admin\":{\"@type\":\"User\",\"name\":\"admin\",\"domainId\":\"#dom\",\"description\":\"Mail administrator\",\"credentials\":{\"0\":{\"@type\":\"Password\",\"secret\":\"$admin_pw\"}}}}}"
  fi
} | plan

# 3a. The mailbox, created once. Its password goes to a file for the owner, never to the screen.
accounts="$(cli query Account --json)"
if ! grep -q "\"emailAddress\":\"$mailbox@$domain\"" <<<"$accounts"; then
  mailbox_pw="$(secret)"
  alias_json=""
  for i in "${!aliases[@]}"; do
    alias_json+="${alias_json:+,}\"$i\":{\"name\":\"${aliases[$i]}\",\"domainId\":\"#dom\"}"
  done
  plan <<EOF
{"@type":"upsert","object":"Domain","matchOn":["name"],"value":{"dom":{"name":"$domain"}}}
{"@type":"create","object":"Account","value":{"mbox":{"@type":"User","name":"$mailbox","domainId":"#dom","aliases":{$alias_json},"credentials":{"0":{"@type":"Password","secret":"$mailbox_pw"}}}}}
EOF
  {
    echo "New mailbox on $host. Save these in your password manager, then delete this file."
    echo
    echo "Email address:  $mailbox@$domain"
    [ "${#aliases[@]}" -gt 0 ] && echo "Also receives:  $(printf '%s@'"$domain"' ' "${aliases[@]}")"
    echo "Password:       $mailbox_pw"
    echo
    echo "Mail app settings: IMAP $host port 993 (SSL/TLS) · SMTP $host port 465 (SSL/TLS) · user = the email address"
    echo "Web admin: https://$host/admin · user admin@$domain · password in env/mail-admin.pw"
  } > env/mail-new-credentials.txt
  unset mailbox_pw
  echo "Created $mailbox@$domain. Its password is in env/mail-new-credentials.txt (root-only)."
fi

# 3b. The certificate from Caddy, registered once. Stalwart reads certificate files when it starts.
restart=0
certificates="$(cli query Certificate --json)"
if [ -s mail-certs/mail.crt ] && ! grep -q "\"$host\"" <<<"$certificates"; then
  plan <<'EOF'
{"@type":"create","object":"Certificate","value":{"cert":{"certificate":{"@type":"File","filePath":"/certs/mail.crt"},"privateKey":{"@type":"File","filePath":"/certs/mail.key"}}}}
{"@type":"update","object":"SystemSettings","value":{"defaultCertificateId":"#cert"}}
EOF
  restart=1
fi

# 3c. Retire the one-time setup login. Switch the tools to the administrator first, so a failure here
#     still leaves a login that works.
if [ "$first_setup" = 1 ]; then
  cli_login "admin@$domain" "$admin_pw"
  sed -i '/^STALWART_RECOVERY_ADMIN=/d' env/mail.env
  dc up -d --force-recreate stalwart
  wait_ready
elif [ "$restart" = 1 ]; then
  dc restart stalwart
  wait_ready
fi
unset admin_pw

# 4. The DNS records to publish, from the server's own zone file.
domain_id="$(cli query Domain --json | python3 -c '
import json, sys
for line in sys.stdin:
    if line.strip():
        d = json.loads(line)
        if d.get("name") == sys.argv[1]:
            print(d["id"])' "$domain")"
echo
echo "DNS records for $domain (add or update them at your DNS host):"
cli get Domain "$domain_id" --json | python3 -c '
import json, re, sys
zone = json.load(sys.stdin).get("dnsZoneFile", "")
zone = re.sub(r"\(\s*((?:\"[^\"]*\"\s*)+)\)", lambda m: " ".join(re.findall(r"\"[^\"]*\"", m.group(1))), zone)
keep = ("._domainkey.", " IN MX ", "_imaps._tcp.", "_submissions._tcp.")
for line in zone.splitlines():
    line = line.strip()
    if not line:
        continue
    name, rest = line.split(None, 1)
    rtype = rest.split()[1] if rest.startswith("IN ") else ""
    if any(k in line for k in keep) or (rtype == "TXT" and "v=spf1" in rest):
        if rtype == "TXT":
            value = "".join(re.findall(r"\"([^\"]*)\"", rest))
            print(f"  TXT  {name}\n       {value}")
        else:
            print(f"  {rtype:<4} {name}  {rest.split(None, 2)[2]}")'
