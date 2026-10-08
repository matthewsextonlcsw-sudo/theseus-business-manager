"""Tests for tools/install_ecc_skills.py (offline: path selection only)."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("install_ecc", ROOT / "tools" / "install_ecc_skills.py")
install_ecc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(install_ecc)


def test_select_paths_keeps_only_chosen_skill_files() -> None:
    tree = [
        {"type": "blob", "path": "skills/seo/SKILL.md"},
        {"type": "blob", "path": "skills/agent-self-evaluation/scripts/evaluate.py"},
        {"type": "tree", "path": "skills/seo"},
        {"type": "blob", "path": "skills/lead-intelligence/SKILL.md"},
        {"type": "blob", "path": "README.md"},
    ]
    chosen = install_ecc.select_paths(tree, ("seo", "agent-self-evaluation"))
    assert chosen == {
        "seo": ["skills/seo/SKILL.md"],
        "agent-self-evaluation": ["skills/agent-self-evaluation/scripts/evaluate.py"],
    }


def test_pin_is_a_full_commit_and_skill_list_is_curated() -> None:
    assert len(install_ecc.ECC_COMMIT) == 40
    assert "lead-intelligence" not in install_ecc.SKILLS
    assert len(install_ecc.SKILLS) == 9
