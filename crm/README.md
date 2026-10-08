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
| Caddy 2.11.6 | HTTPS for all the web addresses; the only service that publishes web ports |
| [Stalwart](https://github.com/stalwartlabs/stalwart) v0.16.25 (optional) | The studio's own email: sends, receives, signs and filters mail; IMAP for your mail app |

## How the connector behaves

- **Form leads** (`POST /lead`): validated, rate-limited per visitor, and filed in Twenty as a person, an opportunity in New, and a note with the inquiry and any intake answers. A hidden spam-trap field quietly drops bots. If Twenty is down, the lead is kept locally and retried every minute; leads are never dropped.
- **Visitor text stays text**: names, answers and messages appear in CRM notes exactly as typed. Links, images and formatting are escaped, so a message can't plant an image that loads when you open the note. The AI summary is escaped the same way.
- **Lead summaries**: the model writes a three-line note (what they want, fit, next step) from the business profile in the knowledge graph. If the model is busy, it retries later.
- **Chat** (`POST /chatwoot/webhook`): every webhook's signature is checked (HMAC-SHA256 over timestamp and body). The connector answers Chatwoot at once and works in the background, so Chatwoot never retries a slow reply.
  - Crisis words get the 988 / 911 message and a person; the model is not asked.
  - "Can I talk to a person?" hands the chat to the inbox.
  - An email or phone number in a chat files a lead.
  - Otherwise the model answers from the business profile. If it doesn't answer in time, the visitor gets a holding message written in advance and the chat goes to a person. It never switches to another model on its own.
  - Every reply is checked before it's sent: anything that looks like a price is replaced, and long replies are cut.
- The bot's rules: says it's an AI, uses only the business facts, never quotes prices or timelines, never promises results, never asks for health details, and treats visitor text as information, not instructions.

## Connect a website

**Form.** Post a normal HTML form to `https://leads.<domain>/lead`. JavaScript is optional: the same endpoint answers JSON.

| Field | |
|---|---|
| `name` | Required |
| `email`, `phone` | At least one. Older forms may send a single `contact` field instead |
| `message` | Optional, up to 2,000 characters |
| `form` | `consultation`, `snapshot` or `chat`; names the lead's source in the CRM |
| `role`, `business`, `city`, `site_url`, `profile_url`, `work_type`, `deadline` | Optional intake answers, stored in the lead's note. Any other field is ignored |
| `website` | The spam trap: hide it from people and leave it empty |
| `return_path` | The form page's own path, e.g. `/contact/` |

Answers:
- **Plain form post:**
  - Success → `303` to `THANKS_URL`.
  - A problem → `303` back to `return_path#form-error` on the site. Browsers send only the site's address across sites, not the page, so the form must name its own page. Only paths on `SITE_ORIGIN` are accepted.
- **JSON post** (`Content-Type: application/json`):
  - Success → `200 {"ok": true}`.
  - A problem → `422 {"errors": {"field": "what to fix"}}`.
  - Too many tries → `429`.

**Chat.** After creating the Website inbox in Chatwoot, load its script on the site:

```html
<script>
  window.chatwootSettings = { position: "right", type: "standard", darkMode: "auto" };
  // Load after the page, so the chat never slows the first view.
  addEventListener("load", () => {
    const s = document.createElement("script");
    s.src = "https://chat.<domain>/packs/js/sdk.js";
    s.async = true;
    s.onload = () => window.chatwootSDK.run({ websiteToken: "<from the inbox>", baseUrl: "https://chat.<domain>" });
    document.body.append(s);
  });
</script>
```

The chat window keeps one cookie, `cw_conversation`, on the website's own domain for 365 days, so a conversation follows the visitor across pages. Say so in the privacy policy.

## Deploy

Everything runs from your own computer with `crm/deploy/deploy.sh`, and nothing changes on the server until you type `yes`.

1. **DNS**: point `crm`, `chat` and `leads` at the server.
2. **Network**: if the model runs on another machine, allow the server to reach the model's port and nothing else.
3. **Settings**: `cp crm/deploy/deploy.env.example crm/deploy/deploy.env` and fill it in. No secrets go in it.
4. `bash crm/deploy/deploy.sh check` is read-only. It shows the server, DNS, free ports and whether the model answers.
5. `bash crm/deploy/deploy.sh up` installs Docker if needed, opens ports 80 and 443, and copies the stack to `REMOTE_DIR`. It creates database passwords on the server (only once), then starts Caddy, Twenty and Chatwoot, and turns on nightly backups.
6. In the browser:
   - **Twenty:** create your login and an API key.
   - **Chatwoot:** create your admin (leave **subscribe to updates** unticked) and a Website inbox, then add a bot with webhook `https://leads.<domain>/chatwoot/webhook` and connect it to the inbox.
7. `bash crm/deploy/deploy.sh connect` asks for the keys at hidden prompts and starts the connector.

**Undo:** `deploy.sh down` stops everything and keeps all data in Docker volumes. **Backups:** nightly at 03:15 into `REMOTE_DIR/backups`. `deploy.sh pull-backups` copies them to `~/mws-crm-backups`, and old ones are never deleted automatically.

## Email (optional)

The studio's own mail server, in the same stack: [Stalwart](https://github.com/stalwartlabs/stalwart) v0.16.25 (open source, AGPL-3.0). It sends and receives mail directly, signs outgoing mail (DKIM), filters spam, and serves your mail app over IMAP. Caddy serves its web admin at `https://<mail host>/admin`, and the mail ports use Caddy's certificate, copied nightly. Stalwart's own docs describe this setup for servers behind Caddy.

**Turn it on (order matters):**
1. **DNS:** add an A record for `MAIL_HOST` (e.g. `mail.example.com`) pointing at the server.
2. **Settings:** fill in `MAIL_HOST`, `MAIL_DOMAIN`, `MAILBOX` and `MAIL_ALIASES` in `deploy.env`.
3. `bash crm/deploy/deploy.sh mail`, then type `yes`. It:
   - opens ports 25, 465 and 993
   - starts Stalwart and creates the mailbox and a mail administrator
   - copies the certificate and turns on the nightly copy
   - prints the DNS records your domain needs
4. **Password:** read the mailbox password once, save it in your password manager, and delete the file. The command to read it is printed at the end.
5. **More DNS:**
   - Add the printed records: MX, SPF for the domain and for the mail host, two DKIM keys, and two SRV records that help mail apps find the server.
   - Keep (or add) a DMARC record.
6. **Reverse DNS:** at your server provider, point the server's IP address back to `MAIL_HOST`. Gmail and Outlook check it.
7. `bash crm/deploy/deploy.sh check` shows the email checks, and your mail app connects with:
   - IMAP: `MAIL_HOST`, port 993, SSL/TLS
   - SMTP: `MAIL_HOST`, port 465, SSL/TLS
   - User name: the full email address

**How it behaves:**
- **DKIM:** one signing key that doesn't change on its own. Your DNS is edited by hand, and Stalwart would otherwise switch to a new key every 90 days that DNS doesn't know about.
- **Certificate:** `mail-cert-sync.sh` copies Caddy's certificate at 03:40 each night. It restarts the mail server (a few seconds) only when the certificate changed, because Stalwart reads certificate files when it starts.
- **Passwords:** all generated on the server and never printed.
  - The administrator's is kept in `env/mail-admin.pw`.
  - The new mailbox's goes to `env/mail-new-credentials.txt` until you delete it.
  - The one-time setup login is retired right after setup, as Stalwart advises.
- **Backups:** the nightly backup includes the mailbox. The mail server pauses for a few seconds so its database is copied whole, and senders retry anything that arrives in that moment. Use `backup.sh <dir> mail` to back up only the mailbox, now.
- **Delivery:** a brand-new mail server has no sending reputation, so its first messages to Gmail or Outlook can land in spam for a few weeks. Check the score with a test service before relying on it.
- **Undo:** `deploy.sh mail-off` stops the mail server, and every message stays. Mail sent to you meanwhile waits at the sender's server and is retried.

**Test:** `sudo bash crm/deploy/test-mail.sh` (Linux with Docker) runs the real setup, certificate and backup scripts as root against a real Stalwart, with a stand-in for Caddy, and sends no mail outside the machine. It makes 12 checks:
- the certificate is copied, owned correctly and served on every mail port
- setup prints no password, and a second run changes nothing
- mail comes in through the alias, goes out signed, and is readable over IMAP
- a renewed certificate takes effect
- the backup is written and the server comes back

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
- **Chatwoot's usage reporting** is switched off (`DISABLE_TELEMETRY=true`). Chatwoot still checks its hub for new versions, sending the installation's id, version and web address, but no counts or chat data (checked in Chatwoot v4.18.0's `lib/chatwoot_hub.rb`).
  - On Chatwoot's first-run page, leave **subscribe to updates** unticked. Ticking it sends your name, company and email to Chatwoot.
- **Cal.diy** (booking) is not included. Its README describes it as for personal, non-production use.
