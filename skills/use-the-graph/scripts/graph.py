#!/usr/bin/env python3
"""Look things up in the business knowledge graph without loading all of it.

Commands:
  graph.py brief "<question>"     the topics and links to read before answering (start here)
  graph.py search "<words>" [-n N] topics ranked by keyword match
  graph.py seeds "<question>"     the closest starter questions and their topics
  graph.py node <id>              one topic in full
  graph.py expand <id>            one topic plus every link to and from it
  graph.py list                   every topic id, type and label

The graph path comes from $THESEUS_GRAPH, else the copy installed next to this skill
(references/business-operating.grag.json), else knowledge/business-operating.grag.json in the repo
that holds this skill. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ALWAYS_APPLY = ("promise_integrity", "unit_economics", "decision_rights")
STOPWORDS = frozenset(
    "a an and are as at be but by can do does for from how i if in into is it its me my of on or our should so "
    "that the their them they this to us was we what when which who why will with you your".split()
)


def graph_path() -> Path:
    env = os.environ.get("THESEUS_GRAPH")
    if env:
        return Path(env).expanduser()
    here = Path(__file__).resolve()
    installed = here.parents[1] / "references" / "business-operating.grag.json"
    if installed.exists():
        return installed
    return here.parents[3] / "knowledge" / "business-operating.grag.json"


def load(path: Path | None = None) -> dict:
    target = path or graph_path()
    if not target.exists():
        sys.exit(f"graph not found: {target} (set THESEUS_GRAPH)")
    return json.loads(target.read_text(encoding="utf-8"))


def words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS and len(w) > 1]


def score_node(node: dict, query: list[str], raw: str) -> float:
    label = set(words(node["label"])) | set(words(node["id"].replace("_", " ")))
    body = words(node["knowledge"])
    score = 3.0 * sum(1 for w in query if w in label)
    score += sum(4.0 for alias in node.get("aliases", []) if alias.lower() in raw)
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


def brief(graph: dict, text: str, max_nodes: int = 4) -> str:
    nodes = by_id(graph)
    picked: list[str] = []
    hints = seeds(graph, text)
    for _, hint in hints:
        for seed in hint["seeds"]:
            if seed not in picked:
                picked.append(seed)
    for _, node in search(graph, text, limit=max_nodes):
        if node["id"] not in picked:
            picked.append(node["id"])
    picked = picked[:max_nodes]
    if not picked:
        return "No topic matched. Run `graph.py list` and pick topics by label, or ask Matthew."

    out = [f"Question: {text}"]
    if hints:
        out.append("Closest starter questions: " + "; ".join(h["ask"] for _, h in hints))
    out.append("Read these topics, then answer with: the constraint, the next move, the failure mode, and the measure.")
    out.append("Always apply: " + ", ".join(f"[{a}]" for a in ALWAYS_APPLY) + ". For licensed or medical clients, also [regulated_clients].\n")
    out.extend(fmt_node(nodes[i]) for i in picked if i in nodes)
    related = [e for e in graph["edges"] if e["source"] in picked or e["target"] in picked]
    out.append("Links:")
    out.extend(fmt_edge(e) for e in related)
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("brief", "seeds"):
        sub.add_parser(name).add_argument("text")
    p_search = sub.add_parser("search")
    p_search.add_argument("text")
    p_search.add_argument("-n", type=int, default=5)
    for name in ("node", "expand"):
        sub.add_parser(name).add_argument("id")
    sub.add_parser("list")
    args = parser.parse_args(argv)

    graph = load()
    nodes = by_id(graph)
    if args.cmd == "brief":
        print(brief(graph, args.text))
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
            print(f"[{node['id']}] {node['type']}: {node['label']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
