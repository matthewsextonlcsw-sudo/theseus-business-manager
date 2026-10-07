# Security

## What never goes in this repo

- API keys, tokens, passwords, or private keys of any kind
- Server addresses, IP addresses, or internal hostnames of a real deployment
- Browser profiles, cookies, or saved sessions
- Customer, client, or patient data of any kind

Configuration uses placeholders such as `STRATA_URL` or `TWENTY_API_KEY`. Real values live in a local `.env` file, which is ignored by git.

`tools/scan-secrets.sh` checks every tracked file before a push and fails if it finds a key-shaped string, a private IP address, or a secret-bearing file.

## Reporting a problem

If you find a secret or personal data in this repo, open a GitHub issue titled "security" without pasting the secret itself, and it will be removed and rotated.
