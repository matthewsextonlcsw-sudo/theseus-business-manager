#!/usr/bin/env bash
# Fails if any tracked or staged file holds a key-shaped string, a private IP address,
# or a secret-bearing file. Run before every push (also installed as a local pre-push hook).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

files=$( { git ls-files; git diff --cached --name-only --diff-filter=ACMR; } | sort -u | grep -v '^tools/scan-secrets.sh$' || true)
[ -z "$files" ] && { echo "scan-secrets: nothing to scan"; exit 0; }

fail=0
report() { echo "BLOCK: $1"; fail=1; }

# Secret-bearing files by name
while IFS= read -r f; do
  case "$f" in
    .env|.env.*) [ "$f" = ".env.example" ] || report "secret file tracked: $f" ;;
    *.pem|*.key|*.p12) report "key file tracked: $f" ;;
  esac
done <<< "$files"

# Key-shaped strings and private addresses
patterns=(
  'sk-[A-Za-z0-9_-]{16,}'
  'ghp_[A-Za-z0-9]{20,}'
  'github_pat_[A-Za-z0-9_]{20,}'
  'xox[abprs]-[A-Za-z0-9-]{10,}'
  'AKIA[0-9A-Z]{16}'
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'
  'Bearer [A-Za-z0-9._~+/-]{20,}'
  '(api[_-]?key|secret|token|password)["'"'"']?[[:space:]]*[:=][[:space:]]*["'"'"'][^"'"'"'$<{ ]{12,}'
  '\b100\.(6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])\.[0-9]{1,3}\.[0-9]{1,3}\b'
  '\b192\.168\.[0-9]{1,3}\.[0-9]{1,3}\b'
  '\b10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\b'
  '\b172\.(1[6-9]|2[0-9]|3[01])\.[0-9]{1,3}\.[0-9]{1,3}\b'
)
for p in "${patterns[@]}"; do
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    if grep -EIqi -- "$p" "$f"; then report "pattern /$p/ in $f"; fi
  done <<< "$files"
done

# Extra blocked strings for a real deployment live in an ignored local file, one regex per line.
if [ -f .scan-secrets.local ]; then
  while IFS= read -r p; do
    [ -z "$p" ] && continue
    while IFS= read -r f; do
      [ -f "$f" ] || continue
      if grep -EIqi -- "$p" "$f"; then report "local rule matched in $f"; fi
    done <<< "$files"
  done < .scan-secrets.local
fi

if [ "$fail" -ne 0 ]; then echo "scan-secrets: FAILED"; exit 1; fi
echo "scan-secrets: clean ($(echo "$files" | wc -l | tr -d ' ') files)"
