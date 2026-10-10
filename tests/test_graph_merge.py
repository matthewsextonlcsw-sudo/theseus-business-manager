"""graph.py across several graph files: discovery, merging, stage briefs and output budgets."""
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "use-the-graph" / "scripts" / "graph.py"
_spec = importlib.util.spec_from_file_location("graph_cli_merge", SCRIPT)
graph_cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(graph_cli)

BUSINESS = ROOT / "knowledge" / "business-operating.grag.json"
CRAFT = ROOT / "knowledge" / "website-craft.grag.json"


@pytest.fixture(scope="module")
def merged() -> dict:
    return graph_cli.load()


def _tiny(node_ids: list[str], edges: list[tuple[str, str]] = ()) -> dict:
    return {
        "graph_meta": {"name": "tiny", "seed_hints": []},
        "nodes": [{"id": i, "type": "craft", "label": i, "aliases": [], "knowledge": f"About {i}."} for i in node_ids],
        "edges": [{"source": s, "target": t, "relation": "uses", "context": "c"} for s, t in edges],
    }


# Discovery ------------------------------------------------------------------------------------------

def test_repo_discovery_finds_active_graphs_and_skips_archives() -> None:
    assert graph_cli.graph_paths() == [BUSINESS, CRAFT]
    assert graph_cli.graph_path() == BUSINESS


def test_installed_layout_wins_and_is_never_mixed_with_the_repo(tmp_path: Path) -> None:
    skill = tmp_path / "use-the-graph"
    (skill / "scripts").mkdir(parents=True)
    (skill / "references").mkdir()
    shutil.copy(SCRIPT, skill / "scripts" / "graph.py")
    for src in (BUSINESS, CRAFT, ROOT / "knowledge" / "business-operating.v1.1.grag.json"):
        shutil.copy(src, skill / "references" / src.name)
    spec = importlib.util.spec_from_file_location("installed_graph", skill / "scripts" / "graph.py")
    installed = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(installed)
    assert [p.name for p in installed.graph_paths()] == ["business-operating.grag.json", "website-craft.grag.json"]
    ids = {n["id"] for n in installed.load()["nodes"]}
    assert {"pricing", "hero_compositions", "regulated_clients", "site_stage_brief"} <= ids


def test_override_accepts_a_comma_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("THESEUS_GRAPH", f" {BUSINESS} , {CRAFT} ")
    assert graph_cli.graph_paths() == [BUSINESS, CRAFT]


@pytest.mark.parametrize("value", [f"{BUSINESS},,{CRAFT}", f"{BUSINESS},/nowhere/missing.grag.json"])
def test_override_rejects_empty_or_missing_entries(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("THESEUS_GRAPH", value)
    with pytest.raises(SystemExit):
        graph_cli.graph_paths()


# Merging --------------------------------------------------------------------------------------------

def test_merge_keeps_provenance_and_resolves_cross_file_links(tmp_path: Path) -> None:
    a, b = tmp_path / "a.grag.json", tmp_path / "b.grag.json"
    a.write_text(json.dumps(_tiny(["one", "two"], [("one", "two")])), encoding="utf-8")
    b.write_text(json.dumps(_tiny(["three"], [("three", "one")])), encoding="utf-8")
    graph = graph_cli.merge([(a, graph_cli.load(a)), (b, graph_cli.load(b))])
    assert [(n["id"], n["source"]) for n in graph["nodes"]] == [("one", "a.grag.json"), ("two", "a.grag.json"), ("three", "b.grag.json")]
    assert len(graph["edges"]) == 2


def test_merge_fails_on_a_duplicate_id_naming_both_files(tmp_path: Path) -> None:
    a, b = tmp_path / "a.grag.json", tmp_path / "b.grag.json"
    a.write_text(json.dumps(_tiny(["same"])), encoding="utf-8")
    b.write_text(json.dumps(_tiny(["same"])), encoding="utf-8")
    with pytest.raises(SystemExit, match="a.grag.json.*b.grag.json"):
        graph_cli.merge([(a, graph_cli.load(a)), (b, graph_cli.load(b))])


def test_merge_fails_on_a_link_to_an_unloaded_topic(tmp_path: Path) -> None:
    a = tmp_path / "a.grag.json"
    a.write_text(json.dumps(_tiny(["one"], [("one", "ghost")])), encoding="utf-8")
    with pytest.raises(SystemExit, match="ghost"):
        graph_cli.merge([(a, graph_cli.load(a))])


# Retrieval over the merged graphs ---------------------------------------------------------------------

@pytest.mark.parametrize(
    "question, expected",
    [
        ("hero image", "hero_compositions"),
        ("font pairing", "type_pairing"),
        ("art direction", "art_direction"),
        ("looks cheap", "looks_cheap_fixes"),
        ("bike shop website", "pattern_trades_repair"),
        ("therapist website", "pattern_clinical_practice"),
        ("which fonts go together for a cafe", "type_pairing"),
        ("the site looks bland and boring", "looks_cheap_fixes"),
        ("restaurant website with a menu", "pattern_restaurant_cafe"),
        ("what colors should the palette use", "color_system"),
        ("check my screenshots against the rubric", "visual_review_rubric"),
        ("how do I make the homepage pop", "art_direction"),
        ("make the design look better", "looks_cheap_fixes"),
        ("they want a discount", "pricing"),
        ("an invoice is overdue", "cash_flow"),
    ],
)
def test_the_right_topic_is_in_the_top_three(merged: dict, question: str, expected: str) -> None:
    top = [n["id"] for _, n in graph_cli.search(merged, question, limit=3)]
    assert expected in top, top


# Stage briefs and budgets ----------------------------------------------------------------------------

def test_stage_brief_leads_with_the_stage_and_stays_on_stage(merged: dict) -> None:
    text = graph_cli.brief(merged, "bike shop hero picture", stage="direction")
    topics = [line.split("]")[0][4:] for line in text.splitlines() if line.startswith("## [")]
    assert topics[0] == "site_stage_direction"
    stage_ids = {n["id"] for n in merged["nodes"] if "direction" in n.get("stages", [])}
    assert set(topics) <= stage_ids | {"regulated_clients", "promise_integrity"}


def test_stage_brief_respects_the_budget_and_never_cuts_a_topic(merged: dict) -> None:
    text = graph_cli.brief(merged, "fonts colors hero pictures layout", stage="sample", budget=1500)
    nodes = graph_cli.by_id(merged)
    shown = [line.split("]")[0][4:] for line in text.splitlines() if line.startswith("## [")]
    for node_id in shown:
        assert nodes[node_id]["knowledge"] in text
    assert graph_cli.estimate_tokens(text) <= 1500 + graph_cli.estimate_tokens(nodes[shown[0]]["knowledge"])
    assert "Also relevant" in text


def test_clinical_questions_always_carry_the_regulated_rules(merged: dict) -> None:
    text = graph_cli.brief(merged, "therapist website colors", stage="direction")
    assert "## [regulated_clients]" in text


def test_generic_words_do_not_pull_in_unrelated_stages(merged: dict) -> None:
    top = [n["id"] for _, n in graph_cli.search(merged, "the site looks bland and boring", limit=3)]
    assert not any(i.startswith("site_stage_") for i in top), top


def test_stage_brief_stays_focused(merged: dict) -> None:
    text = graph_cli.brief(merged, "bike shop website, needs a strong hero picture", stage="direction")
    shown = [line.split("]")[0][4:] for line in text.splitlines() if line.startswith("## [")]
    assert shown[:2] == ["site_stage_direction", "pattern_trades_repair"]
    assert len(shown) <= 5 and "pattern_retail_shop" not in shown
    assert graph_cli.estimate_tokens(text) <= graph_cli.DEFAULT_BUDGET


def test_links_are_capped(merged: dict) -> None:
    text = graph_cli.brief(merged, "build a website for a bike shop", stage="brief")
    links = [line for line in text.splitlines() if line.startswith("- [")]
    assert len(links) <= graph_cli.MAX_LINKS


def test_unknown_stage_is_reported(merged: dict) -> None:
    assert "Unknown stage" in graph_cli.brief(merged, "anything", stage="party")


def test_stages_command_lists_the_gates(capsys: pytest.CaptureFixture[str]) -> None:
    assert graph_cli.main(["stages"]) == 0
    out = capsys.readouterr().out
    assert out.index("brief") < out.index("direction") < out.index("handoff")
    assert "Matthew picks one of two routes" in out


def test_list_can_filter_by_stage(capsys: pytest.CaptureFixture[str]) -> None:
    assert graph_cli.main(["list", "--stage", "review"]) == 0
    out = capsys.readouterr().out
    assert "[visual_review_rubric]" in out and "[pricing]" not in out
