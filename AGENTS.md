# Agents working in this repo

## Building or reviewing a website

Follow `knowledge/website-craft.md`, the website craft playbook. Work its seven stages in order (brief, direction, copy, sample, build, review, handoff) and stop at every gate for Matthew's approval. Read only the topics for the stage you are in.

- Never invent facts, reviews, people, prices, or pictures of the business.
- For therapists and clinics, the regulated-client rules in `knowledge/business-operating.grag.json` (topic `regulated_clients`) override every design preference.
- Judge design from screenshots you have actually looked at, at 390x844 and 1280x800.

The playbook is generated: edit the topic files in `knowledge/website-craft/`, then run `python3 tools/build_craft_graph.py`.

## Before you open a PR

```bash
python3 -m pytest
python3 tools/check-graph.py knowledge/*.grag.json
python3 tools/build_craft_graph.py --check
bash tools/scan-secrets.sh
```
