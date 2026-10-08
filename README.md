# Theseus Business Manager

An open-source AI business manager for a small studio, built to run on a **local model**.

Theseus keeps the pipeline moving, drafts follow-ups and proposals, runs the weekly business review, answers website chats, and builds solid small-business websites. It works from a knowledge graph of sales, marketing, website and customer-service practice, and it drafts anything that leaves the building for a human to approve.

It was built for [MWS Consulting](https://mwsconsulting.studio) and released under the MIT license so other small studios can run their own.

> **Status: early.** Knowledge graph v1.2 is in (44 topics). The skills, browser setup, website starter and CRM stack are being built in the open. See [docs/ROADMAP.md](docs/ROADMAP.md).

## What's in here

| Folder | What it holds | Status |
|---|---|---|
| `knowledge/` | The business knowledge graph (JSON) and its schema | v1.2 done |
| `skills/` | Agent skills (`SKILL.md` folders): running the business, using the graph, building websites, browsing | In progress |
| `tools/` | Graph checker and pre-push secret scanner | Done |
| `starter/` | An Astro starter for standard small-business sites | Planned |
| `crm/` | A self-hosted CRM stack (Twenty + Chatwoot + a small connector) as an open GoHighLevel-style alternative | Planned |

## How it fits together

- **Model:** any OpenAI-compatible local model. Built and tested on Qwen3.8-Flash-Next served by Strata.
- **Harness:** skills are plain `SKILL.md` folders, written for the DSH NEXT agent harness and readable by any harness that loads that format.
- **Knowledge:** the graph in `knowledge/`, small enough to give the model in full.
- **Tools:** a real browser it drives through a CLI, and the CRM's API.

## Ground rules Theseus follows

- It drafts messages, proposals and prices. A human approves before anything is sent, spent, priced or promised.
- It never invents numbers, reviews, testimonials or results.
- Web pages are information to it, never instructions.
- It does not solve CAPTCHAs or disguise itself to get past bot checks. When a site challenges it, it stops and asks.
- For licensed and regulated clients (therapists, medical practices), their professional rules come first. That covers testimonials, patient data and outcome claims.

## Install into DSH NEXT

```bash
bash tools/install-dsh-next.sh        # copies skills + graph into ~/.dsh-next/skills
```

Then append the section in [brief/business-manager.md](brief/business-manager.md) to the agent's standing brief (`~/.dsh-next/AGENTS.md`), with your business name. Other harnesses that read `SKILL.md` folders can load the same `skills/` directory.

### Skills from ECC

Nine skills come from [ECC](https://github.com/affaan-m/ECC) (MIT), pinned to one commit and downloaded at install time rather than copied here: `hipaa-compliance`, `healthcare-phi-compliance`, `seo`, `design-system`, `frontend-a11y`, `email-ops`, `market-research`, `brand-voice`, `agent-self-evaluation`.

```bash
python3 tools/install_ecc_skills.py   # installs them next to Theseus's own skills, with ECC's license
```

They were picked because they are small, work in any harness, and fit a small studio. ECC skills that depend on Claude Code features or paid prospecting services were left out.

### The browser

Theseus's browser is [agent-browser](https://github.com/vercel-labs/agent-browser). Install it once with `npm install -g agent-browser && agent-browser install`. Chrome can't start inside a sandboxed agent shell, so start the browser once from a normal terminal:

```bash
~/.dsh-next/skills/browse-like-a-person/scripts/browser start
```

The agent's commands then drive that window through a control socket.

## Checking the work

```bash
python3 tools/check-graph.py knowledge/*.grag.json   # graph structure
python3 -m pytest tests/                             # tests
bash tools/scan-secrets.sh                           # no keys, IPs or secret files before a push
```

## License

MIT. See [LICENSE](LICENSE).
