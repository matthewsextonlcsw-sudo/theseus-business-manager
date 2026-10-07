"""Tests for tools/migrate_v1_2.py: the committed graph must match what the script builds."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("migrate_v1_2", ROOT / "tools" / "migrate_v1_2.py")
migrate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migrate)


def test_committed_graph_matches_script() -> None:
    committed = json.loads((ROOT / "knowledge" / "business-operating.grag.json").read_text(encoding="utf-8"))
    assert committed == migrate.build(), "run: python3 tools/migrate_v1_2.py"


def test_v1_1_source_is_untouched() -> None:
    original = json.loads(migrate.SOURCE.read_text(encoding="utf-8"))
    assert original["graph_meta"]["version"] == "1.1"
    assert len(original["nodes"]) == 25


def test_v1_2_contents() -> None:
    graph = migrate.build()
    ids = {n["id"] for n in graph["nodes"]}
    for node_id in ("studio_profile", "decision_rights", "regulated_clients", "website_build_process", "site_qa_launch"):
        assert node_id in ids
    relations = {(e["source"], e["target"]): e["relation"] for e in graph["edges"]}
    assert relations[("pricing", "positioning")] == "can_undermine"
    assert graph["graph_meta"]["version"] == "1.2"
    assert graph["graph_meta"]["profile_node"] == "studio_profile"


def test_no_prices_in_profile() -> None:
    profile = next(n for n in migrate.build()["nodes"] if n["id"] == "studio_profile")
    assert "$" not in profile["knowledge"], "the profile must not carry prices"
