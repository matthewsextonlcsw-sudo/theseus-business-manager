#!/usr/bin/env python3
"""Look things up in the knowledge graphs without loading all of them.

Commands:
  graph.py brief "<question>"                  the topics and links to read before answering (start here)
  graph.py brief --stage <stage> "<question>"  website work: only the current stage's topics
  graph.py stages                              the website stages, their topics and gates
  graph.py search "<words>" [-n N]             topics ranked by keyword match
  graph.py seeds "<question>"                  the closest starter questions and their topics
  graph.py node <id>                           one topic in full
  graph.py expand <id>                         one topic plus every link to and from it
  graph.py list [--stage <stage>]              every topic id, type and label

Graphs: every active *.grag.json (archives named *.v1.* are skipped) in the references/ folder installed next
to this skill, else in the knowledge/ folder of the repo that holds it. $THESEUS_GRAPH overrides that with one
path or a comma-separated list. Briefs keep to a budget (about 2,500 tokens by default, at about four characters
per token) and never cut a topic in half. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ALWAYS_APPLY = ("promise_integrity", "unit_economics", "decision_rights")
ARCHIVE_MARK = ".v1."
BUSINESS_FILE = "business-operating.grag.json"
DEFAULT_BUDGET = 2500
LINK_RESERVE = 250  # tokens kept back from the budget for the Links list
MAX_LINKS = 8
# Words too common in website questions to say which topic is meant; they still count in aliases and bodies.
GENERIC = frozenset({"site", "sites", "website", "websites", "web", "page", "pages"})
CLINICAL = re.compile(
    r"therap|counsel|clinic|medical|health|patient|psych|social work|dental|dentist|chiro|physio|doctor|nurse|wellness",
    re.IGNORECASE,
)
STOPWORDS = frozenset(
    "a an and are as at be but by can do does for from how i if in into is it its me my of on or our should so "
    "that the their them they this to us was we what when which who why will with you your".split()
)


def estimate_tokens(text: str) -> int:
    """Rough token count for budgets: about four characters per token."""
    return len(text) // 4 + 1


def _active(folder: Path) -> list[Path]:
    return sorted(p for p in folder.glob("*.grag.json") if ARCHIVE_MARK not in p.name)


def graph_paths() -> list[Path]:
    env = os.environ.get("THESEUS_GRAPH")
    if env:
        parts = [part.strip() for part in env.split(",")]
        if not all(parts):
            sys.exit(f"THESEUS_GRAPH has an empty entry: {env!r}")
        paths = [Path(part).expanduser() for part in parts]
        for path in paths:
            if not path.exists():
                sys.exit(f"graph not found: {path} (named in THESEUS_GRAPH)")
        return paths
    here = Path(__file__).resolve()
    installed = here.parents[1] / "references"
    found = _active(installed) if installed.is_dir() else []
    return found or _active(here.parents[3] / "knowledge")


def graph_path() -> Path:
    """The business graph, for callers that read only one file."""
    paths = graph_paths()
    return next((p for p in paths if p.name == BUSINESS_FILE), paths[0])


def load(path: Path | None = None) -> dict:
    """One graph file when given a path; otherwise every active graph, merged."""
    if path is None:
        paths = graph_paths()
        if not paths:
            sys.exit("no graph found (set THESEUS_GRAPH)")
        return merge([(p, load(p)) for p in paths])
    if not path.exists():
        sys.exit(f"graph not found: {path} (set THESEUS_GRAPH)")
    return json.loads(path.read_text(encoding="utf-8"))


def merge(graphs: list[tuple[Path, dict]]) -> dict:
    nodes, edges, hints, usage, stages, owner = [], [], [], [], [], {}
    for path, graph in graphs:
        meta = graph.get("graph_meta", {})
        for node in graph["nodes"]:
            if node["id"] in owner:
                sys.exit(f"duplicate topic id {node['id']} in {owner[node['id']]} and {path.name}")
            owner[node["id"]] = path.name
            nodes.append({**node, "source": path.name})
        edges.extend(graph["edges"])
        hints.extend(meta.get("seed_hints", []))
        if meta.get("usage"):
            usage.append(f"{meta.get('name', path.name)}: {meta['usage']}")
        stages = stages or meta.get("stages", [])
    for edge in edges:
        for end in ("source", "target"):
            if edge[end] not in owner:
                sys.exit(f"link {edge['source']} -> {edge['target']} names {edge[end]}, a topic in no loaded graph")
    meta = {"name": "merged", "sources": [p.name for p, _ in graphs], "usage": "\n".join(usage),
            "seed_hints": hints, "stages": stages}
    return {"graph_meta": meta, "nodes": nodes, "edges": edges}


def words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS and len(w) > 1]


def score_node(node: dict, query: list[str], raw: str) -> float:
    label = (set(words(node["label"])) | set(words(node["id"].replace("_", " ")))) - GENERIC
    body = words(node["knowledge"])
    score = 3.0 * sum(1 for w in query if w in label)
    asked = set(query)
    for alias in node.get("aliases", []):
        phrase = alias.lower()
        if phrase in raw:
            score += 4.0
        elif len(set(words(phrase))) >= 2 and set(words(phrase)) <= asked:
            score += 3.0  # every word of the phrase is in the question, in any order ("make it pop")
    score += min(4.0, 0.5 * sum(body.count(w) for w in query))
    return score


def search(graph: dict, text: str, limit: int = 5) -> list[tuple[float, dict]]:
    query, raw = words(text), text.lower()
    ranked = sorted(((score_node(n, query, raw), n) for n in graph["nodes"]), key=lambda x: -x[0])
    return [(s, n) for s, n in ranked if s > 0][:limit]


def seeds(graph: dict, text: str, limit: int = 2) -> list[tuple[float, dict]]:
    query = set(words(text))
    ranked = []
    for hint in graph["graph_meta"].get("seed_hints", []):
        ask = set(words(hint["ask"]))
        overlap = len(query & ask) / max(1, len(ask | query))
        ranked.append((overlap, hint))
    ranked.sort(key=lambda x: -x[0])
    return [(s, h) for s, h in ranked if s >= 0.2][:limit]


def by_id(graph: dict) -> dict[str, dict]:
    return {n["id"]: n for n in graph["nodes"]}


def links(graph: dict, node_id: str) -> list[dict]:
    return [e for e in graph["edges"] if node_id in (e["source"], e["target"])]


def fmt_node(node: dict) -> str:
    return f"## [{node['id']}] {node['label']} ({node['type']})\n{node['knowledge']}\n"


def fmt_edge(edge: dict) -> str:
    return f"- [{edge['source']}] {edge['relation']} [{edge['target']}]: {edge['context']}"


def _pick(graph: dict, text: str, max_nodes: int, stage: str | None) -> list[str]:
    nodes = by_id(graph)
    picked: list[str] = []
    allowed = None
    if stage:
        allowed = {n["id"] for n in graph["nodes"] if stage in n.get("stages", [])}
        if f"site_stage_{stage}" in nodes:
            picked.append(f"site_stage_{stage}")
        if CLINICAL.search(text) and "regulated_clients" in nodes:
            picked.append("regulated_clients")
    for _, hint in seeds(graph, text):
        picked += [s for s in hint["seeds"] if s in nodes and s not in picked and (allowed is None or s in allowed)]
    for _, node in search(graph, text, limit=len(graph["nodes"])):
        if node["id"] not in picked and (allowed is None or node["id"] in allowed):
            picked.append(node["id"])
    fixed = 1 + ("regulated_clients" in picked[:2]) if stage else 0  # the stage topic and, for clinics, its rules
    return picked[: fixed + max_nodes]


def brief(graph: dict, text: str, max_nodes: int = 4, stage: str | None = None, budget: int = DEFAULT_BUDGET) -> str:
    nodes = by_id(graph)
    stages = {s["stage"]: s for s in graph["graph_meta"].get("stages", [])}
    if stage and stage not in stages:
        known = ", ".join(stages) or "none loaded"
        return f"Unknown stage '{stage}'. Stages: {known}. Run `graph.py stages`."
    picked = _pick(graph, text, max_nodes, stage)
    if not picked:
        return "No topic matched. Run `graph.py list` and pick topics by label, or ask Matthew."

    out = [f"Question: {text}"]
    if stage:
        order = list(stages)
        out.append(f"Stage {order.index(stage) + 1} of {len(order)}: {stage}. Gate: {stages[stage]['gate']}.")
        out.append("Read these topics and apply them to this stage only. Overrides: [promise_integrity]; for licensed "
                   "or medical clients, [regulated_clients].\n")
    else:
        hints = seeds(graph, text)
        if hints:
            out.append("Closest starter questions: " + "; ".join(h["ask"] for _, h in hints))
        out.append("Read these topics, then answer with: the constraint, the next move, the failure mode, and the measure.")
        out.append("Always apply: " + ", ".join(f"[{a}]" for a in ALWAYS_APPLY)
                   + ". For licensed or medical clients, also [regulated_clients].\n")

    used = estimate_tokens("\n".join(out))
    shown, deferred = [], []
    for node_id in picked:
        cost = estimate_tokens(fmt_node(nodes[node_id]))
        if shown and used + cost > budget - LINK_RESERVE:
            deferred.append(node_id)
            continue
        shown.append(node_id)
        used += cost
    out.extend(fmt_node(nodes[i]) for i in shown)
    if deferred:
        out.append("Also relevant (read with `graph.py node <id>`): " + ", ".join(f"[{i}]" for i in deferred) + "\n")

    inside = [e for e in graph["edges"] if e["source"] in shown and e["target"] in shown]
    outward = [e for e in graph["edges"] if (e["source"] in shown) != (e["target"] in shown)]
    related = (inside + outward)[:MAX_LINKS]
    out.append("Links:")
    out.extend(fmt_edge(e) for e in related)
    return "\n".join(out)


def stage_table(graph: dict) -> str:
    stages = graph["graph_meta"].get("stages", [])
    if not stages:
        return "No staged graph loaded."
    lines = []
    for i, s in enumerate(stages, 1):
        count = sum(1 for n in graph["nodes"] if s["stage"] in n.get("stages", []))
        lines.append(f"{i}. {s['stage']:<9} start with [{s['topic']}], {count} topics. Gate: {s['gate']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_brief = sub.add_parser("brief")
    p_brief.add_argument("text")
    p_brief.add_argument("--stage")
    p_brief.add_argument("--budget", type=int, default=DEFAULT_BUDGET, help="about how many tokens to print")
    sub.add_parser("seeds").add_argument("text")
    p_search = sub.add_parser("search")
    p_search.add_argument("text")
    p_search.add_argument("-n", type=int, default=5)
    for name in ("node", "expand"):
        sub.add_parser(name).add_argument("id")
    sub.add_parser("list").add_argument("--stage")
    sub.add_parser("stages")
    args = parser.parse_args(argv)

    graph = load()
    nodes = by_id(graph)
    if args.cmd == "brief":
        print(brief(graph, args.text, stage=args.stage, budget=args.budget))
    elif args.cmd == "search":
        for score, node in search(graph, args.text, args.n):
            print(f"{score:5.1f}  [{node['id']}] {node['label']}")
    elif args.cmd == "seeds":
        for score, hint in seeds(graph, args.text):
            print(f"{score:4.2f}  {hint['ask']}  ->  {', '.join(hint['seeds'])}")
    elif args.cmd in ("node", "expand"):
        if args.id not in nodes:
            print(f"unknown topic: {args.id} (run `graph.py list`)", file=sys.stderr)
            return 2
        print(fmt_node(nodes[args.id]))
        if args.cmd == "expand":
            print("Links:")
            print("\n".join(fmt_edge(e) for e in links(graph, args.id)))
    elif args.cmd == "list":
        for node in graph["nodes"]:
            if args.stage is None or args.stage in node.get("stages", []):
                print(f"[{node['id']}] {node['type']}: {node['label']}")
    elif args.cmd == "stages":
        print(stage_table(graph))
    return 0


if __name__ == "__main__":
    sys.exit(main())
