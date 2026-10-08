#!/usr/bin/env bash
# Deploy the CRM stack to a server you own. A reviewed script: nothing changes until you type "yes".
#
#   bash crm/deploy/deploy.sh check          read-only look at the server, DNS, ports and model access
#   bash crm/deploy/deploy.sh up             install Docker if needed, open 80/443, start Caddy, Twenty, Chatwoot, backups
#   bash crm/deploy/deploy.sh connect        ask for API keys (hidden), then start the connector
#   bash crm/deploy/deploy.sh status         what is running and whether the sites answer
#   bash crm/deploy/deploy.sh pull-backups   copy the server's database backups to this computer
#   bash crm/deploy/deploy.sh down           stop the stack (data stays)
#
# Settings come from crm/deploy/deploy.env (copy deploy.env.example). Secrets never go in that file:
# database passwords are generated on the server once, and API keys are asked for at hidden prompts.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
CONFIG="$HERE/deploy.env"
[ -f "$CONFIG" ] || { echo "Missing $CONFIG. Copy deploy.env.example to deploy.env and fill it in."; exit 2; }
set -a
# shellcheck disable=SC1090
. "$CONFIG"
set +a

for v in DEPLOY_SSH REMOTE_DIR CRM_HOST CHAT_HOST LEADS_HOST ACME_EMAIL SITE_ORIGIN THANKS_URL BRAIN_URL BRAIN_MODEL; do
  [ -n "${!v:-}" ] || { echo "deploy.env: $v is empty"; exit 2; }
done
case "$CRM_HOST $CHAT_HOST $LEADS_HOST $ACME_EMAIL" in
  *example.com*) echo "deploy.env still has example.com values"; exit 2 ;;
esac
case "$REMOTE_DIR" in
  /opt/virgo-factory*|/|/opt|/opt/) echo "Refusing REMOTE_DIR=$REMOTE_DIR"; exit 2 ;;
  /opt/?*) ;;
  *) echo "REMOTE_DIR must be a folder under /opt"; exit 2 ;;
esac

DEPLOY_DIR="$REMOTE_DIR/crm/deploy"
remote() { ssh -o BatchMode=yes -o ConnectTimeout=10 "$DEPLOY_SSH" "$@"; }
confirm() {
  printf '\n%s\n\nType yes to continue: ' "$1"
  read -r answer
  [ "$answer" = "yes" ] || { echo "Stopped. Nothing changed."; exit 1; }
}

cmd_check() {
  echo "== Server"
  remote 'hostname; . /etc/os-release; echo "$PRETTY_NAME"; free -h | awk "/Mem/ {print \"memory available: \" \$7}"; df -h / | awk "NR==2 {print \"disk free: \" \$4}"'
  echo "== Docker"
  remote 'docker --version 2>/dev/null || echo "not installed (up installs it)"'
  echo "== DNS (each name must point at the server)"
  server_ip=$(remote "ip -4 route get 1.1.1.1 | awk '{for (i=1;i<=NF;i++) if (\$i==\"src\") print \$(i+1)}'")
  echo "server address: $server_ip"
  for host in "$CRM_HOST" "$CHAT_HOST" "$LEADS_HOST"; do
    resolved=$(dig +short A "$host" | tail -1)
    if [ "$resolved" = "$server_ip" ]; then echo "ok    $host -> $resolved"; else echo "WAIT  $host -> ${resolved:-nothing yet}"; fi
  done
  echo "== Ports 80 and 443 on the server (should be free before the first up)"
  remote 'ss -tlnH "( sport = :80 or sport = :443 )" | awk "{print \$4}"' | sed 's/^/in use: /' || true
  echo "== Model reachable from the server (an HTTP check of /models, no AI run)"
  code=$(remote "curl -s -o /dev/null -w '%{http_code}' --max-time 6 '$BRAIN_URL/models'" || true)
  case "$code" in
    200|401) echo "ok    the model server answers (HTTP $code)" ;;
    *) echo "WAIT  no answer from the model server (HTTP ${code:-none}); check the network rule between the servers" ;;
  esac
}

write_env_files() {
  remote "set -e; mkdir -p '$DEPLOY_DIR/env'; cd '$DEPLOY_DIR'; umask 077
    printf 'CRM_HOST=%s\nCHAT_HOST=%s\nLEADS_HOST=%s\nACME_EMAIL=%s\n' '$CRM_HOST' '$CHAT_HOST' '$LEADS_HOST' '$ACME_EMAIL' > env/caddy.env
    if [ ! -f env/twenty.env ]; then
      pg=\$(openssl rand -hex 24); key=\$(openssl rand -base64 32)
      printf 'POSTGRES_PASSWORD=%s\nPG_DATABASE_URL=postgres://postgres:%s@twenty-db:5432/default\nSERVER_URL=https://%s\nENCRYPTION_KEY=%s\n' \"\$pg\" \"\$pg\" '$CRM_HOST' \"\$key\" > env/twenty.env
      echo 'created env/twenty.env (new database password and encryption key)'
    fi
    if [ ! -f env/chatwoot.env ]; then
      skb=\$(openssl rand -hex 64); pg=\$(openssl rand -hex 24); rp=\$(openssl rand -hex 24)
      printf 'SECRET_KEY_BASE=%s\nFRONTEND_URL=https://%s\nPOSTGRES_PASSWORD=%s\nREDIS_PASSWORD=%s\nENABLE_ACCOUNT_SIGNUP=false\nFORCE_SSL=false\nRAILS_LOG_TO_STDOUT=true\nLOG_LEVEL=info\nACTIVE_STORAGE_SERVICE=local\n' \"\$skb\" '$CHAT_HOST' \"\$pg\" \"\$rp\" > env/chatwoot.env
      echo 'created env/chatwoot.env (new secrets)'
    fi
    [ -f env/connector.env ] || : > env/connector.env"
}

install_backups() {
  remote "set -e
    cat > /etc/systemd/system/mws-crm-backup.service <<UNIT
[Unit]
Description=CRM database backups
[Service]
Type=oneshot
ExecStart=$DEPLOY_DIR/backup.sh $REMOTE_DIR
UNIT
    cat > /etc/systemd/system/mws-crm-backup.timer <<UNIT
[Unit]
Description=Nightly CRM database backups
[Timer]
OnCalendar=*-*-* 03:15:00
Persistent=true
[Install]
WantedBy=timers.target
UNIT
    chmod +x '$DEPLOY_DIR/backup.sh'
    systemctl daemon-reload
    systemctl enable --now mws-crm-backup.timer"
}

cmd_up() {
  confirm "This will, on $DEPLOY_SSH:
  - install Docker if it is missing (apt: docker.io, docker-compose-v2)
  - open ports 80 and 443 in the firewall (ufw)
  - copy this stack to $REMOTE_DIR (nothing else on the server is touched)
  - create database passwords and keys on the server, only if they don't exist yet
  - start Caddy, Twenty and Chatwoot, prepare Chatwoot's database, and turn on nightly backups
Undo: bash crm/deploy/deploy.sh down (stops everything, keeps the data)."
  remote 'command -v docker >/dev/null || (apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq docker.io docker-compose-v2)'
  remote 'docker compose version'
  remote 'ufw allow 80/tcp >/dev/null && ufw allow 443/tcp >/dev/null && ufw allow 443/udp >/dev/null && ufw status | head -8'
  remote "mkdir -p '$REMOTE_DIR'"
  rsync -az --exclude '.venv' --exclude '__pycache__' --exclude '.pytest_cache' --exclude '.coverage' \
    --exclude 'deploy.env' --exclude 'env/' "$ROOT/crm" "$DEPLOY_SSH:$REMOTE_DIR/"
  rsync -az "$ROOT/knowledge" "$DEPLOY_SSH:$REMOTE_DIR/"
  write_env_files
  remote "cd '$DEPLOY_DIR' && docker compose pull --quiet && docker compose up -d"
  echo "Preparing Chatwoot's database (first run takes a few minutes)..."
  remote "cd '$DEPLOY_DIR' && docker compose run --rm chatwoot-rails bundle exec rails db:chatwoot_prepare"
  echo "Waiting for Twenty to report healthy..."
  remote "cd '$DEPLOY_DIR' && for i in \$(seq 1 60); do
      [ \"\$(docker inspect -f '{{.State.Health.Status}}' \$(docker compose ps -q twenty-server))\" = healthy ] && { echo 'Twenty is healthy'; exit 0; }
      sleep 5; done; echo 'Twenty is not healthy yet: run status'; exit 1"
  install_backups
  cat <<NEXT

Stack is up. Next, in your browser:
  1. https://$CRM_HOST   create your Twenty login, then Settings > API & Webhooks > create an API key.
  2. https://$CHAT_HOST  create your Chatwoot admin, then add a Website inbox for $SITE_ORIGIN.
     Settings > Bots > Add bot: webhook URL https://$LEADS_HOST/chatwoot/webhook. Keep its access token and secret.
     Connect the bot to the Website inbox.
  3. Then run: bash crm/deploy/deploy.sh connect
NEXT
}

cmd_connect() {
  confirm "This writes the connector's settings on the server and starts it.
You will be asked for four values; nothing you type is shown or saved on this computer."
  read -rsp "Twenty API key: " twenty_key; echo
  read -rp "Chatwoot account id (the number in the Chatwoot address bar): " cw_account
  read -rsp "Chatwoot bot access token: " cw_token; echo
  read -rsp "Chatwoot bot webhook secret: " cw_secret; echo
  if [ -n "${BRAIN_API_KEY_CMD:-}" ]; then
    brain_key=$(eval "$BRAIN_API_KEY_CMD")
  else
    read -rsp "Model API key: " brain_key; echo
  fi
  for v in twenty_key cw_account cw_token cw_secret brain_key; do
    [ -n "${!v}" ] || { echo "A value was empty. Nothing changed."; exit 1; }
  done
  printf 'TWENTY_API_KEY=%s\nCHATWOOT_ACCOUNT_ID=%s\nCHATWOOT_BOT_TOKEN=%s\nCHATWOOT_WEBHOOK_SECRET=%s\nBRAIN_URL=%s\nBRAIN_API_KEY=%s\nBRAIN_MODEL=%s\nALLOWED_ORIGINS=%s\nTHANKS_URL=%s\n' \
    "$twenty_key" "$cw_account" "$cw_token" "$cw_secret" "$BRAIN_URL" "$brain_key" "$BRAIN_MODEL" "$SITE_ORIGIN" "$THANKS_URL" \
    | remote "umask 077 && cat > '$DEPLOY_DIR/env/connector.env'"
  unset twenty_key cw_token cw_secret brain_key
  remote "cd '$DEPLOY_DIR' && docker compose --profile connector build --quiet connector && docker compose --profile connector up -d connector"
  echo "Checking the connector..."
  for _ in $(seq 1 20); do
    if curl -fsS --max-time 5 "https://$LEADS_HOST/health" >/dev/null 2>&1; then echo "ok    https://$LEADS_HOST/health"; return 0; fi
    sleep 3
  done
  echo "The connector is not answering yet. Run: bash crm/deploy/deploy.sh status"
}

cmd_status() {
  remote "cd '$DEPLOY_DIR' && docker compose --profile connector ps --format 'table {{.Service}}\t{{.Status}}'"
  for url in "https://$CRM_HOST/healthz" "https://$CHAT_HOST/" "https://$LEADS_HOST/health"; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "$url" || true)
    echo "HTTP ${code:-none}  $url"
  done
}

cmd_pull_backups() {
  dest="$HOME/mws-crm-backups"
  mkdir -p "$dest"
  rsync -az "$DEPLOY_SSH:$REMOTE_DIR/backups/" "$dest/"
  echo "Backups copied to $dest"
  ls -1 "$dest" | tail -6
}

cmd_down() {
  confirm "This stops every service in the stack on $DEPLOY_SSH. All data stays in Docker volumes; run up to start again."
  remote "cd '$DEPLOY_DIR' && docker compose --profile connector down"
}

case "${1:-check}" in
  check) cmd_check ;;
  up) cmd_up ;;
  connect) cmd_connect ;;
  status) cmd_status ;;
  pull-backups) cmd_pull_backups ;;
  down) cmd_down ;;
  *) echo "usage: deploy.sh check|up|connect|status|pull-backups|down"; exit 2 ;;
esac
