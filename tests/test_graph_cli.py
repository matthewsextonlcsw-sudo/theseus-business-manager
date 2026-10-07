"""Tests for skills/use-the-graph/scripts/graph.py against the shipped v1.2 graph."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("graph_cli", ROOT / "skills" / "use-the-graph" / "scripts" / "graph.py")
graph_cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(graph_cli)


@pytest.fixture(scope="module")
def graph() -> dict:
    return graph_cli.load(ROOT / "knowledge" / "business-operating.grag.json")


def test_default_path_points_at_repo_graph() -> None:
    assert graph_cli.graph_path() == ROOT / "knowledge" / "business-operating.grag.json"


def test_search_finds_pricing_for_discount(graph: dict) -> None:
    top = [n["id"] for _, n in graph_cli.search(graph, "they want a discount", limit=3)]
    assert "pricing" in top


def test_seeds_match_new_lead(graph: dict) -> None:
    hints = graph_cli.seeds(graph, "a new lead just came in from the website")
    assert hints and "speed_to_lead" in hints[0][1]["seeds"]


def test_brief_is_bounded_and_names_overrides(graph: dict) -> None:
    text = graph_cli.brief(graph, "a therapist wants a website with a chat bot")
    assert text.count("\n## [") <= 4
    assert "[regulated_clients]" in text
    assert "[decision_rights]" in text


def test_brief_without_match_says_so(graph: dict) -> None:
    assert "No topic matched" in graph_cli.brief(graph, "zzqx")


def test_unknown_node_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    assert graph_cli.main(["node", "not_a_topic"]) == 2
    assert "unknown topic" in capsys.readouterr().err


def test_expand_lists_links(capsys: pytest.CaptureFixture[str]) -> None:
    assert graph_cli.main(["expand", "pricing"]) == 0
    out = capsys.readouterr().out
    assert "[unit_economics] constrains [pricing]" in out
