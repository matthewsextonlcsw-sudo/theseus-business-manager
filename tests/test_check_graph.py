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


def test_shipped_graphs_pass_together() -> None:
    # The README command: active graphs are checked as one set, the archived v1.1 on its own.
    paths = [str(p) for p in sorted((ROOT / "knowledge").glob("*.grag.json"))]
    assert len(paths) == 3
    assert check_graph.check_set(paths) is True


def _named(tmp_path: Path, name: str, graph: dict) -> str:
    path = tmp_path / name
    path.write_text(json.dumps(graph), encoding="utf-8")
    return str(path)


def test_cross_file_links_pass_when_checked_together(tmp_path: Path) -> None:
    a = _named(tmp_path, "a.grag.json", {"nodes": [_node("one"), _node("two")], "edges": [_edge("one", "two")]})
    b = _named(tmp_path, "b.grag.json", {"nodes": [_node("three")], "edges": [_edge("three", "one")]})
    assert check_graph.check(b) is False
    assert check_graph.check_set([a, b]) is True


def test_duplicate_ids_across_active_files_fail(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    a = _named(tmp_path, "a.grag.json", {"nodes": [_node("one"), _node("two")], "edges": [_edge("one", "two")]})
    b = _named(tmp_path, "b.grag.json", {"nodes": [_node("one"), _node("three")], "edges": [_edge("one", "three")]})
    assert check_graph.check_set([a, b]) is False
    assert "a.grag.json" in capsys.readouterr().out


def test_archives_are_checked_on_their_own(tmp_path: Path) -> None:
    active = _named(tmp_path, "g.grag.json", {"nodes": [_node("one"), _node("two")], "edges": [_edge("one", "two")]})
    archive = _named(tmp_path, "g.v1.1.grag.json", {"nodes": [_node("one"), _node("two")], "edges": [_edge("two", "one")]})
    assert check_graph.check_set([active, archive]) is True
