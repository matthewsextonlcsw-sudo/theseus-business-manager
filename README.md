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

## Checking the work

```bash
python3 tools/check-graph.py knowledge/*.grag.json   # graph structure
python3 -m pytest tests/                             # tests
bash tools/scan-secrets.sh                           # no keys, IPs or secret files before a push
```

## License

MIT. See [LICENSE](LICENSE).
