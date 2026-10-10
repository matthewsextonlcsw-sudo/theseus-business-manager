#!/usr/bin/env python3
"""Compile the website craft topics into the graph Theseus reads and a plain playbook any AI can read.

The source of truth is knowledge/website-craft/*.md: one topic per file, a small header and a plain body,
easy to read and edit by hand (it also opens as an Obsidian vault). This script writes:

  knowledge/website-craft.grag.json   the graph, same shape as business-operating.grag.json
  knowledge/website-craft.md          the playbook: every topic in stage order, for droids and other agents

Usage:
  python3 tools/build_craft_graph.py           rebuild both files
  python3 tools/build_craft_graph.py --check   exit 1 if either file is out of date

Topic header (between --- lines): id, label, type, stages (comma list), aliases (comma list), links
(one per line: "- target | relation | context"). Links may point at business-graph topics.
Standard library only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOPICS = ROOT / "knowledge" / "website-craft"
BUSINESS = ROOT / "knowledge" / "business-operating.grag.json"
GRAPH_OUT = ROOT / "knowledge" / "website-craft.grag.json"
PLAYBOOK_OUT = ROOT / "knowledge" / "website-craft.md"

STAGES = ("brief", "direction", "copy", "sample", "build", "review", "handoff")
TYPES = ("process", "craft", "check", "pattern", "reference")
GATES = {
    "brief": "Matthew approves brief.md",
    "direction": "Matthew picks one of two routes",
    "copy": "Matthew approves the sitemap and copy",
    "sample": "Matthew approves the rendered hero and next section",
    "build": "no gate; go to review",
    "review": "rubric passes and every check is green",
    "handoff": "publishing needs Matthew's separate OK",
}
FIELDS = ("id", "label", "type", "stages", "aliases")

META = {
    "name": "MWS website craft graph",
    "version": "1.0",
    "checked": "2026-10-10",
    "purpose": (
        "How Theseus and other agents build small-business websites that are distinctive, fast, accessible and "
        "truthful: the stages and gates, the design decisions, the failures to catch, and the review rubric."
    ),
    "usage": (
        "Work one stage at a time and read only that stage's topics: graph.py brief --stage <stage> \"<question>\". "
        "Read the project's state file first and resume at its stage. Gates need Matthew's approval in words, recorded "
        "in the state file; silence is never approval. promise_integrity and regulated_clients (business graph) override "
        "every design preference. Never invent facts, reviews, people, or pictures of the business. Judge design from "
        "screenshots you have actually seen."
    ),
    "changelog": (
        "1.0 (2026-10-10): first version. 42 topics distilled, in original wording, from Anthropic's frontend-design "
        "skill, taste-skill, Impeccable, Vercel's Web Interface Guidelines, UI UX Pro Max, gogh's conflict resolutions, "
        "WCAG 2.2 and web.dev, plus the MWS Consulting site as the studio reference."
    ),
    "sources": [
        "github.com/anthropics/skills (frontend-design, Apache-2.0)",
        "github.com/Leonxlnx/taste-skill (MIT)",
        "github.com/pbakaus/impeccable (Apache-2.0)",
        "github.com/vercel-labs/web-interface-guidelines (MIT)",
        "github.com/nextlevelbuilder/ui-ux-pro-max-skill (MIT)",
        "github.com/AgriciDaniel/gogh (Apache-2.0)",
        "github.com/emilkowalski/skills (MIT)",
        "w3.org/TR/WCAG22 and its understanding documents",
        "web.dev (LCP, responsive images, font best practices)",
    ],
    "seed_hints": [
        {"ask": "Build a website for a new client.", "seeds": ["site_stage_brief", "site_project_state", "design_read"]},
        {"ask": "Show me two design directions.", "seeds": ["site_stage_direction", "art_direction", "hero_compositions"]},
        {"ask": "The site looks bland, cheap or generic.", "seeds": ["looks_cheap_fixes", "anti_slop", "art_direction"]},
        {"ask": "Which fonts should the site use?", "seeds": ["type_pairing", "type_scale_hierarchy", "font_loading"]},
        {"ask": "Make or choose the hero picture.", "seeds": ["hero_compositions", "imagery_sourcing", "image_art_direction"]},
        {"ask": "Pick the colors.", "seeds": ["color_system", "contrast_checks"]},
        {"ask": "Write the homepage copy.", "seeds": ["site_stage_copy", "site_copy_voice", "hero_first_screen"]},
        {"ask": "Review my screenshots.", "seeds": ["site_stage_review", "visual_review_rubric", "looks_cheap_fixes"]},
        {"ask": "Website for a bike shop or repair shop.", "seeds": ["pattern_trades_repair", "hero_compositions"]},
        {"ask": "Website for a therapist or clinic.", "seeds": ["pattern_clinical_practice", "regulated_clients"]},
        {"ask": "Website for a restaurant or cafe.", "seeds": ["pattern_restaurant_cafe", "imagery_sourcing"]},
        {"ask": "Where were we on this site?", "seeds": ["site_project_state"]},
    ],
}


class TopicError(ValueError):
    """A topic file is malformed or points somewhere that does not exist."""


def estimate_tokens(text: str) -> int:
    """Rough token count used for retrieval budgets: about four characters per token."""
    return len(text) // 4 + 1


def _split_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def parse_topic(text: str, filename: str) -> tuple[dict, list[dict]]:
    lines = text.splitlines()
    stripped = [line.strip() for line in lines]
    if not lines or stripped[0] != "---" or "---" not in stripped[1:]:
        raise TopicError(f"{filename}: the header must sit between two --- lines")
    end = 1 + stripped[1:].index("---")
    header, body = lines[1:end], "\n".join(lines[end + 1 :]).strip()

    fields: dict[str, str] = {}
    raw_links: list[str] = []
    in_links = False
    for line in header:
        if not line.strip():
            continue
        if in_links and line.lstrip().startswith("- "):
            raw_links.append(line.lstrip()[2:])
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise TopicError(f"{filename}: cannot read header line {line!r}")
        key, value = key.strip(), value.strip()
        in_links = key == "links"
        if key != "links":
            fields[key] = value

    for field in FIELDS:
        if not fields.get(field):
            raise TopicError(f"{filename}: missing '{field}'")
    if fields["type"] not in TYPES:
        raise TopicError(f"{filename}: unknown type {fields['type']!r}; use one of {', '.join(TYPES)}")
    stages = _split_list(fields["stages"])
    unknown = [s for s in stages if s not in STAGES]
    if unknown:
        raise TopicError(f"{filename}: unknown stage {', '.join(unknown)}; use {', '.join(STAGES)}")
    if not body:
        raise TopicError(f"{filename}: the body is empty")

    node = {
        "id": fields["id"],
        "type": fields["type"],
        "label": fields["label"],
        "aliases": _split_list(fields["aliases"]),
        "stages": stages,
        "knowledge": body,
    }
    links = []
    for raw in raw_links:
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) != 3 or not all(parts):
            raise TopicError(f"{filename}: a link must read '- target | relation | context', got {raw!r}")
        links.append({"source": node["id"], "target": parts[0], "relation": parts[1], "context": parts[2]})
    return node, links


def read_topics(folder: Path = TOPICS) -> list[tuple[dict, list[dict]]]:
    topics, seen = [], {}
    for path in sorted(folder.glob("*.md")):
        node, links = parse_topic(path.read_text(encoding="utf-8"), path.name)
        if path.stem != node["id"]:
            raise TopicError(f"{path.name}: the file name must be the topic id ({node['id']}.md)")
        if node["id"] in seen:
            raise TopicError(f"duplicate topic id {node['id']} in {seen[node['id']]} and {path.name}")
        seen[node["id"]] = path.name
        topics.append((node, links))
    return topics


def _order(node: dict) -> tuple:
    stage_topics = [f"site_stage_{s}" for s in STAGES]
    if node["id"] in stage_topics:
        return (0, stage_topics.index(node["id"]), node["id"])
    return (1, TYPES.index(node["type"]), node["id"])


def _business_ids() -> set[str]:
    graph = json.loads(BUSINESS.read_text(encoding="utf-8"))
    return {n["id"] for n in graph["nodes"]}


def build_graph(folder: Path = TOPICS, known_ids: set[str] | None = None) -> dict:
    topics = read_topics(folder)
    known = (_business_ids() if known_ids is None else set(known_ids)) | {node["id"] for node, _ in topics}
    edges = []
    for node, links in topics:
        for link in links:
            if link["target"] not in known:
                raise TopicError(f"{node['id']}.md links to {link['target']}, which is not a topic in either graph")
            edges.append(link)
    meta = dict(META)
    meta["stages"] = [{"stage": s, "topic": f"site_stage_{s}", "gate": GATES[s]} for s in STAGES]
    return {
        "graph_meta": meta,
        "nodes": sorted((node for node, _ in topics), key=_order),
        "edges": sorted(edges, key=lambda e: (e["source"], e["target"], e["relation"])),
    }


def build_playbook(folder: Path = TOPICS) -> str:
    graph = build_graph(folder)
    out = [
        "# Website craft playbook",
        "",
        "Generated from `knowledge/website-craft/` by `tools/build_craft_graph.py`. Do not edit by hand.",
        "",
        "For any agent that builds or reviews a website in this repo: follow the stages in order, read the topics for",
        "the stage you are in, and stop at every gate for Matthew's approval. Theseus reads the same topics through",
        "`skills/use-the-graph/scripts/graph.py brief --stage <stage> \"<question>\"`.",
        "",
        "Rules that override everything here: never invent facts, reviews, people or pictures of the business",
        "(promise_integrity); for therapists and clinics, the regulated-client rules win (regulated_clients).",
        "",
        "## Stages and gates",
        "",
        "| # | Stage | Topic | Gate |",
        "|---|---|---|---|",
    ]
    for i, stage in enumerate(graph["graph_meta"]["stages"], 1):
        out.append(f"| {i} | {stage['stage']} | {stage['topic']} | {stage['gate']} |")
    out.append("")
    links = {}
    for edge in graph["edges"]:
        links.setdefault(edge["source"], []).append(f"{edge['relation']} {edge['target']}")
    headings = {"process": "Process", "craft": "Craft", "check": "Checks", "pattern": "Business patterns", "reference": "References"}
    current = None
    for node in graph["nodes"]:
        if node["type"] != current:
            current = node["type"]
            out += [f"## {headings[current]}", ""]
        out += [
            f"### {node['label']} ({node['id']})",
            "",
            f"Stages: {', '.join(node['stages'])}",
            "",
            node["knowledge"],
            "",
            f"Links: {'; '.join(links.get(node['id'], []))}",
            "",
        ]
    out.append(f"Sources: {'; '.join(graph['graph_meta']['sources'])}. Checked {graph['graph_meta']['checked']}.")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    check = "--check" in (argv if argv is not None else sys.argv[1:])
    try:
        graph_text = json.dumps(build_graph(), indent=2, ensure_ascii=False) + "\n"
        playbook_text = build_playbook()
    except TopicError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if check:
        stale = [p.name for p, text in ((GRAPH_OUT, graph_text), (PLAYBOOK_OUT, playbook_text))
                 if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            print(f"out of date: {', '.join(stale)} (run: python3 tools/build_craft_graph.py)")
            return 1
        print("website craft graph and playbook are up to date")
        return 0
    GRAPH_OUT.write_text(graph_text, encoding="utf-8")
    PLAYBOOK_OUT.write_text(playbook_text, encoding="utf-8")
    graph = json.loads(graph_text)
    print(f"wrote {GRAPH_OUT.name} ({len(graph['nodes'])} topics, {len(graph['edges'])} links) and {PLAYBOOK_OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
