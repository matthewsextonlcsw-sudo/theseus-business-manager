"""Tests for tools/check-graph.py."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("check_graph", ROOT / "tools" / "check-graph.py")
check_graph = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_graph)


def _write(tmp_path: Path, graph: dict) -> str:
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(graph), encoding="utf-8")
    return str(path)


def _node(node_id: str) -> dict:
    return {"id": node_id, "type": "domain", "label": node_id.title(), "aliases": [], "knowledge": "Some rules."}


def _edge(source: str, target: str) -> dict:
    return {"source": source, "target": target, "relation": "feeds", "context": "Why they connect."}


def test_valid_graph_passes(tmp_path: Path) -> None:
    graph = {
        "graph_meta": {"seed_hints": [{"ask": "q", "seeds": ["a"]}]},
        "nodes": [_node("a"), _node("b")],
        "edges": [_edge("a", "b")],
    }
    assert check_graph.check(_write(tmp_path, graph)) is True


@pytest.mark.parametrize(
    "graph",
    [
        {"nodes": [_node("a"), _node("a")], "edges": [_edge("a", "a")]},
        {"nodes": [_node("a"), _node("b")], "edges": [_edge("a", "missing")]},
        {"graph_meta": {"seed_hints": [{"ask": "q", "seeds": ["ghost"]}]}, "nodes": [_node("a"), _node("b")], "edges": [_edge("a", "b")]},
        {"nodes": [_node("a"), _node("b"), _node("lonely")], "edges": [_edge("a", "b")]},
        {"nodes": [_node("a"), _node("b")], "edges": [_edge("a", "b"), _edge("a", "b")]},
    ],
    ids=["duplicate-id", "dangling-edge", "missing-seed", "isolated-node", "duplicate-edge"],
)
def test_broken_graphs_fail(tmp_path: Path, graph: dict) -> None:
    assert check_graph.check(_write(tmp_path, graph)) is False


def test_shipped_graphs_pass() -> None:
    for path in sorted((ROOT / "knowledge").glob("*.grag.json")):
        assert check_graph.check(str(path)) is True, path.name
