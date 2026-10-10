#!/usr/bin/env python3
"""Validate knowledge graph files: unique ids, no edge or seed hint pointing at a missing node, no isolated nodes.

Usage: python3 tools/check-graph.py knowledge/*.grag.json
Active graphs are checked together as one set, because they may link to each other (the website craft graph
links into the business graph). Archived graphs (file names containing ".v1.") are checked on their own.
Exit code 1 when any check fails.
"""
import collections
import json
import sys
from pathlib import Path

ARCHIVE_MARK = ".v1."


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _errors(graphs: list[tuple[str, dict]]) -> list[str]:
    errors = []
    owner: dict[str, str] = {}
    nodes, edges, hints = [], [], []
    for path, graph in graphs:
        name = Path(path).name
        for n in graph.get("nodes", []):
            node_id = n.get("id")
            if node_id in owner:
                where = name if owner[node_id] == name else f"{owner[node_id]} and {name}"
                errors.append(f"duplicate node id: {node_id} ({where})")
            owner.setdefault(node_id, name)
            nodes.append(n)
        edges.extend(graph.get("edges", []))
        hints.extend(graph.get("graph_meta", {}).get("seed_hints", []))
    known = set(owner)

    for n in nodes:
        for field in ("id", "type", "label", "knowledge"):
            if not n.get(field):
                errors.append(f"node {n.get('id', '?')} is missing '{field}'")
    for e in edges:
        for end in ("source", "target"):
            if e.get(end) not in known:
                errors.append(f"edge {e.get('source')} -> {e.get('target')} names a missing {end}")
        if not e.get("relation") or not e.get("context"):
            errors.append(f"edge {e.get('source')} -> {e.get('target')} needs a relation and a context")
    pairs = collections.Counter((e.get("source"), e.get("target"), e.get("relation")) for e in edges)
    for pair, count in pairs.items():
        if count > 1:
            errors.append(f"duplicate edge: {pair}")
    for hint in hints:
        for seed in hint.get("seeds", []):
            if seed not in known:
                errors.append(f"seed hint '{hint.get('ask')}' names a missing node: {seed}")

    degree = collections.Counter()
    for e in edges:
        degree[e.get("source")] += 1
        degree[e.get("target")] += 1
    for n in nodes:
        if degree[n.get("id")] == 0:
            errors.append(f"node has no edges: {n.get('id')}")
    return errors


def _report(label: str, graphs: list[tuple[str, dict]], errors: list[str]) -> bool:
    for path, graph in graphs:
        nodes, edges = graph.get("nodes", []), graph.get("edges", [])
        words = sum(len(n.get("knowledge", "").split()) for n in nodes)
        words += sum(len(e.get("context", "").split()) for e in edges)
        print(f"{path}: {len(nodes)} nodes, {len(edges)} edges, ~{int(words * 1.35)} tokens")
    print(f"{label}: {'OK' if not errors else 'FAILED'}")
    for err in errors:
        print("  - " + err)
    return not errors


def check(path: str) -> bool:
    """Check one graph file on its own."""
    graphs = [(path, _load(path))]
    return _report(path, graphs, _errors(graphs))


def check_set(paths: list[str]) -> bool:
    """Check archives one by one and every active graph together as one set."""
    archives = [p for p in paths if ARCHIVE_MARK in Path(p).name]
    active = [p for p in paths if p not in archives]
    results = [check(p) for p in archives]
    if active:
        graphs = [(p, _load(p)) for p in active]
        names = ", ".join(Path(p).name for p in active)
        results.append(_report(f"active set ({names})", graphs, _errors(graphs)))
    return all(results)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(0 if check_set(sys.argv[1:]) else 1)
