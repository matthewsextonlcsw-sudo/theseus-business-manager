#!/usr/bin/env bash
# One far end of the private WireGuard link: a host that offers ONE service to the CRM server.
# Runs on that host as root; deploy.sh link sends it over ssh. This host calls out to the server, so
# nothing opens on its router or firewall. A relay on the link address passes only TARGET, the firewall
# allows only that port from the server, and if Docker runs here, the link can't open new connections
# into its containers. Keeps its private key across runs; prints its public key last.
#
# Env: SERVER (the CRM server's public IP), PORT (its UDP port), PEER (its public key),
#      ADDR (this host's link address), PEER_ADDR (the server's link address),
#      TARGET (ip:port to pass on), NAME (a label for the relay, e.g. model or crm)
set -euo pipefail

: "${SERVER:?}" "${PORT:?}" "${PEER:?}" "${ADDR:?}" "${PEER_ADDR:?}" "${TARGET:?}"
NAME="${NAME:-service}"
tport="${TARGET##*:}"

command -v wg >/dev/null || {
  apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq wireguard-tools >/dev/null
}
umask 077
mkdir -p /etc/wireguard
[ -s /etc/wireguard/wg-crm.key ] || wg genkey > /etc/wireguard/wg-crm.key

# Docker publishes ports through its own forwarding rules, ahead of ufw. Refuse new connections from the
# link into containers; replies to connections this host makes are unaffected.
guard=""
if command -v docker >/dev/null && iptables -n -L DOCKER-USER >/dev/null 2>&1; then
  guard="PostUp = iptables -I DOCKER-USER -i %i -m conntrack --ctstate NEW -j DROP
PostDown = iptables -D DOCKER-USER -i %i -m conntrack --ctstate NEW -j DROP"
fi

cat > /etc/wireguard/wg-crm.conf <<CONF
# Private link to the CRM server: this host calls out, and only $TARGET is passed on. See deploy.sh link.
[Interface]
Address = $ADDR/32
PrivateKey = $(cat /etc/wireguard/wg-crm.key)
$guard

[Peer]
PublicKey = $PEER
Endpoint = $SERVER:$PORT
AllowedIPs = $PEER_ADDR/32
PersistentKeepalive = 25
CONF

umask 022
cat > /etc/systemd/system/wg-crm-relay.socket <<UNIT
[Unit]
Description=Relay for the CRM server over wg-crm ($NAME, one port)
[Socket]
ListenStream=$ADDR:$tport
FreeBind=true
[Install]
WantedBy=sockets.target
UNIT
cat > /etc/systemd/system/wg-crm-relay.service <<UNIT
[Unit]
Description=Relay for the CRM server: $ADDR:$tport -> $TARGET ($NAME)
Requires=wg-crm-relay.socket
After=wg-crm-relay.socket
[Service]
ExecStart=/usr/lib/systemd/systemd-socket-proxyd $TARGET
DynamicUser=yes
UNIT

ufw allow in on wg-crm from "$PEER_ADDR" to "$ADDR" port "$tport" proto tcp comment "CRM server -> $NAME relay" >/dev/null
systemctl daemon-reload
systemctl enable wg-quick@wg-crm >/dev/null 2>&1
systemctl restart wg-quick@wg-crm
systemctl enable wg-crm-relay.socket >/dev/null 2>&1
systemctl restart wg-crm-relay.socket
wg pubkey < /etc/wireguard/wg-crm.key
