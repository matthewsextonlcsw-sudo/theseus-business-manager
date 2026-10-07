#!/usr/bin/env python3
"""Validate a knowledge graph file: unique ids, no edge or seed hint pointing at a missing node.

Usage: python3 tools/check-graph.py knowledge/business-operating.grag.json [more files...]
Exit code 1 when any file has a structural error.
"""
import collections
import json
import sys


def check(path: str) -> bool:
    with open(path, encoding="utf-8") as fh:
        graph = json.load(fh)
    errors = []
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    ids = [n.get("id") for n in nodes]
    known = set(ids)

    for node_id, count in collections.Counter(ids).items():
        if count > 1:
            errors.append(f"duplicate node id: {node_id}")
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
    for hint in graph.get("graph_meta", {}).get("seed_hints", []):
        for seed in hint.get("seeds", []):
            if seed not in known:
                errors.append(f"seed hint '{hint.get('ask')}' names a missing node: {seed}")

    degree = collections.Counter()
    for e in edges:
        degree[e.get("source")] += 1
        degree[e.get("target")] += 1
    isolated = [i for i in ids if degree[i] == 0]
    for node_id in isolated:
        errors.append(f"node has no edges: {node_id}")

    words = sum(len(n.get("knowledge", "").split()) for n in nodes)
    words += sum(len(e.get("context", "").split()) for e in edges)
    status = "OK" if not errors else "FAILED"
    print(f"{path}: {status} | {len(nodes)} nodes, {len(edges)} edges, ~{int(words * 1.35)} tokens")
    for err in errors:
        print("  - " + err)
    return not errors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    results = [check(p) for p in sys.argv[1:]]
    sys.exit(0 if all(results) else 1)
