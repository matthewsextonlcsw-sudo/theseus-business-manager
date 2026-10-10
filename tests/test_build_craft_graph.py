"""Tests for tools/build_craft_graph.py: the website craft graph is compiled from readable topic files."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("build_craft_graph", ROOT / "tools" / "build_craft_graph.py")
craft = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(craft)

TOPIC = """---
id: demo_topic
label: Demo topic
type: craft
stages: direction, review
aliases: demo, sample topic
links:
- other_topic | uses | Because it needs it.
---
Body text.

More body.
"""


def test_parse_topic_reads_header_and_body() -> None:
    node, links = craft.parse_topic(TOPIC, "demo_topic.md")
    assert node == {
        "id": "demo_topic",
        "type": "craft",
        "label": "Demo topic",
        "aliases": ["demo", "sample topic"],
        "stages": ["direction", "review"],
        "knowledge": "Body text.\n\nMore body.",
    }
    assert links == [{"source": "demo_topic", "target": "other_topic", "relation": "uses", "context": "Because it needs it."}]


@pytest.mark.parametrize(
    "broken, message",
    [
        (TOPIC.replace("id: demo_topic\n", ""), "missing 'id'"),
        (TOPIC.replace("stages: direction, review", "stages: direction, launch-party"), "unknown stage"),
        (TOPIC.replace("- other_topic | uses | Because it needs it.", "- other_topic uses"), "link"),
        (TOPIC.replace("---\nid", "id", 1), "header"),
        (TOPIC.replace("type: craft", "type: vibes"), "unknown type"),
    ],
)
def test_parse_topic_rejects_broken_files(broken: str, message: str) -> None:
    with pytest.raises(craft.TopicError, match=message):
        craft.parse_topic(broken, "demo_topic.md")


def test_file_name_must_match_id(tmp_path: Path) -> None:
    (tmp_path / "wrong_name.md").write_text(TOPIC, encoding="utf-8")
    with pytest.raises(craft.TopicError, match="file name"):
        craft.read_topics(tmp_path)


def test_links_must_reach_a_known_topic(tmp_path: Path) -> None:
    (tmp_path / "demo_topic.md").write_text(TOPIC, encoding="utf-8")
    with pytest.raises(craft.TopicError, match="other_topic"):
        craft.build_graph(tmp_path, known_ids=set())


def test_committed_graph_and_playbook_match_the_topics() -> None:
    committed = json.loads((ROOT / "knowledge" / "website-craft.grag.json").read_text(encoding="utf-8"))
    assert committed == craft.build_graph(), "run: python3 tools/build_craft_graph.py"
    playbook = (ROOT / "knowledge" / "website-craft.md").read_text(encoding="utf-8")
    assert playbook == craft.build_playbook(), "run: python3 tools/build_craft_graph.py"


def test_every_stage_has_its_stage_topic_in_order() -> None:
    graph = craft.build_graph()
    ids = [n["id"] for n in graph["nodes"]]
    stage_ids = [f"site_stage_{s}" for s in craft.STAGES]
    assert [i for i in ids if i in stage_ids] == stage_ids
    nexts = {(e["source"], e["target"]) for e in graph["edges"] if e["relation"] == "next"}
    for here, there in zip(stage_ids, stage_ids[1:]):
        assert (here, there) in nexts


def test_topics_are_small_enough_for_a_local_model() -> None:
    # A stage brief has a budget of about 2,500 tokens and should fit at least three whole topics.
    for node in craft.build_graph()["nodes"]:
        assert craft.estimate_tokens(node["knowledge"]) <= 700, node["id"]


def test_every_topic_is_reachable_by_stage_and_words() -> None:
    for node in craft.build_graph()["nodes"]:
        assert node["stages"], node["id"]
        assert len(node["aliases"]) >= 3, node["id"]
