# Knowledge

Theseus's knowledge is two small graphs in JSON, loaded together. Each **node** is one topic with the rules a practical expert would apply. Each **edge** says how two topics affect each other, with a sentence of context. Edges may cross from one graph to the other.

| File | What it is |
|---|---|
| `business-operating.v1.1.grag.json` | The original BusinessMasteryGraphRAG (25 topics), kept unchanged as an archive |
| `business-operating.grag.json` | v1.2.1, the business graph: 44 topics, 128 links, about 14K tokens |
| `website-craft.grag.json` | v1.0, the website craft graph: 42 topics, about 150 links, about 14K tokens |
| `website-craft/` | The craft graph's source: one readable topic per file (also opens as an Obsidian vault) |
| `website-craft.md` | The craft playbook: every topic in stage order, for droids and other agents |

The business graph is generated from v1.1 by `tools/migrate_v1_2.py`, so every change is readable in one place. It adds a business profile, the manager's operating rhythm and decision rights, cash flow, delivery, scope, capacity, CRM upkeep, speed to lead, local visibility, reviews, managed AI delivery, rules for regulated clients, and website building. Rules from outside sources (Google, the FTC, NASW, WCAG, Core Web Vitals) were checked against those sources on 2026-10-07. Version 1.2.1 (2026-10-10) points its website build process at the craft graph's stages.

To run a different business, replace the `studio_profile` node with your own public facts.

## The website craft graph

How to build a small-business site that is distinctive, fast, accessible and truthful, in seven stages with gates: brief, direction (two routes), copy, a rendered sample, build, review, handoff. Each stage has a topic (`site_stage_brief` ... `site_stage_handoff`), and every topic is tagged with the stages it serves, so a local model reads only what the current stage needs.

To change a topic, edit its file in `website-craft/` and rebuild:

```bash
python3 tools/build_craft_graph.py           # writes website-craft.grag.json and website-craft.md
python3 tools/build_craft_graph.py --check   # fails if either file is out of date
```

A topic file has a header between `---` lines (`id`, `label`, `type`, `stages`, `aliases`, and `links`, one per line as `- target | relation | context`) and a plain body. Keep a topic under about 700 tokens so a stage brief fits three or more.

Credits: the craft topics are original writing that distills public guidance from Anthropic's frontend-design skill (Apache-2.0), taste-skill (MIT), Impeccable (Apache-2.0), Vercel's Web Interface Guidelines (MIT), UI UX Pro Max (MIT), gogh's conflict resolutions (Apache-2.0) and emilkowalski/skills (MIT), plus WCAG 2.2 and web.dev. Each topic names its sources and the date they were checked.

## Shape

```json
{
  "graph_meta": { "name": "...", "version": "...", "usage": "...", "seed_hints": [{ "ask": "...", "seeds": ["node_id"] }] },
  "nodes": [{ "id": "pricing", "type": "skill", "label": "Pricing and discounts", "aliases": ["discount"], "knowledge": "..." }],
  "edges": [{ "source": "unit_economics", "target": "pricing", "relation": "constrains", "context": "..." }]
}
```

Craft nodes also carry `stages`, and the craft graph's `graph_meta` lists the stages with their gates.

## How a model should use it

Use `skills/use-the-graph/scripts/graph.py`. It finds every active graph (files with `.v1.` in the name are archives and are skipped) and merges them; `$THESEUS_GRAPH` can name one file or a comma-separated list instead.

- Business questions: `graph.py brief "<question>"`, then answer with the constraint, the next move, the failure mode and the measure.
- Website work: `graph.py brief --stage <stage> "<question>"` returns the stage's own topic first, then the most relevant topics tagged for that stage, plus the regulated-client rules whenever the question is about a clinic or therapist.

Briefs keep to a budget (about 2,500 tokens by default, at about four characters per token), never cut a topic in half, list the topics that did not fit under "Also relevant", and show at most eight links. `promise_integrity` and `unit_economics` overrule the business topics; `regulated_clients` overrules every design preference.

## Checking it

```bash
python3 tools/check-graph.py knowledge/*.grag.json
```

Active graphs are checked together, because they link to each other; the archive is checked on its own. The check fails on duplicate ids (across files too), edges or seed hints that name a missing topic, duplicate edges, and topics with no edges.
