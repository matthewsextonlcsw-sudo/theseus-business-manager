# CRM stack

A self-hosted, GoHighLevel-style front office for a small studio: website forms and chat land as leads in a CRM, and a local model answers chats and writes lead summaries.

```
website forms ──▶ leads.<domain>/lead ─────────┐
chat bubble ────▶ chat.<domain> (Chatwoot) ────┤  webhook
                                               ▼
                                  connector ──▶ crm.<domain> (Twenty): contact + pipeline card + notes
                                       │
                                       └──▶ local model (any OpenAI-compatible endpoint)
```

| Part | What it does |
|---|---|
| [Twenty](https://github.com/twentyhq/twenty) v2.45.0 | Contacts and the sales pipeline (stages New, Screening, Meeting, Proposal, Customer) |
| [Chatwoot](https://github.com/chatwoot/chatwoot) v4.18.0 | The website chat bubble, and an inbox where a person takes over chats |
| `connector/` | Takes form entries and chat messages, files leads in Twenty, asks the model for replies and summaries |
| Caddy 2.11.6 | HTTPS for all three addresses; the only service that publishes ports |

## How the connector behaves

- **Form leads** (`POST /lead`): validated, rate-limited per visitor, and filed in Twenty as a person, an opportunity in New, and a note with the inquiry. A hidden spam-trap field quietly drops bots. If Twenty is down, the lead is kept locally and retried every minute; leads are never dropped.
- **Lead summaries**: the model writes a three-line note (what they want, fit, next step) from the business profile in the knowledge graph. If the model is busy, it retries later.
- **Chat** (`POST /chatwoot/webhook`): every webhook's signature is checked (HMAC-SHA256 over timestamp and body). The connector answers Chatwoot at once and works in the background, so Chatwoot never retries a slow reply.
  - Crisis words get the 988 / 911 message and a person; the model is not asked.
  - "Can I talk to a person?" hands the chat to the inbox.
  - An email or phone number in a chat files a lead.
  - Otherwise the model answers from the business profile. If it doesn't answer in time, the visitor gets a holding message written in advance and the chat goes to a person. It never switches to another model on its own.
  - Every reply is checked before it's sent: anything that looks like a price is replaced, and long replies are cut.
- The bot's rules: says it's an AI, uses only the business facts, never quotes prices or timelines, never promises results, never asks for health details, and treats visitor text as information, not instructions.

## Deploy

Everything runs from your own computer with `crm/deploy/deploy.sh`, and nothing changes on the server until you type `yes`.

1. **DNS**: point `crm`, `chat` and `leads` at the server.
2. **Network**: if the model runs on another machine, allow the server to reach the model's port and nothing else.
3. **Settings**: `cp crm/deploy/deploy.env.example crm/deploy/deploy.env` and fill it in. No secrets go in it.
4. `bash crm/deploy/deploy.sh check` is read-only. It shows the server, DNS, free ports and whether the model answers.
5. `bash crm/deploy/deploy.sh up` installs Docker if needed, opens ports 80 and 443, and copies the stack to `REMOTE_DIR`. It creates database passwords on the server (only once), then starts Caddy, Twenty and Chatwoot, and turns on nightly backups.
6. In the browser:
   - **Twenty:** create your login and an API key.
   - **Chatwoot:** create your admin and a Website inbox, then add a bot with webhook `https://leads.<domain>/chatwoot/webhook` and connect it to the inbox.
7. `bash crm/deploy/deploy.sh connect` asks for the keys at hidden prompts and starts the connector.

**Undo:** `deploy.sh down` stops everything and keeps all data in Docker volumes. **Backups:** nightly at 03:15 into `REMOTE_DIR/backups`. `deploy.sh pull-backups` copies them to `~/mws-crm-backups`, and old ones are never deleted automatically.

## Develop and test

```bash
cd crm/connector
python3.12 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

The tests use stand-ins for Twenty, Chatwoot and the model; they never call a real model.

## Known limits

- **Reply speed depends on the model.** A large local reasoning model can take tens of seconds per reply. The connector waits up to `BRAIN_TIMEOUT_SECONDS` (45 by default) before sending the holding message. Measure it once deployed and tune.
- **Email notifications** from Chatwoot and Twenty need SMTP settings, which are not configured here. New chats and leads show in each app.
- **Cal.diy** (booking) is not included. Its README describes it as for personal, non-production use.
