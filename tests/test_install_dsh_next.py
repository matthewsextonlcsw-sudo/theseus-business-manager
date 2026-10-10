"""tools/install-dsh-next.sh into a throwaway DSH home: both graphs and the playbook must reach Theseus."""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_install_carries_both_graphs_and_the_playbook(tmp_path: Path) -> None:
    env = {**os.environ, "DSH_HOME": str(tmp_path)}
    env.pop("THESEUS_GRAPH", None)
    run = subprocess.run(["bash", str(ROOT / "tools" / "install-dsh-next.sh")], env=env, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr

    skills = tmp_path / "skills"
    refs = sorted(p.name for p in (skills / "use-the-graph" / "references").glob("*.grag.json"))
    assert refs == ["business-operating.grag.json", "website-craft.grag.json"]
    assert (skills / "build-a-site" / "references" / "website-craft.md").is_file()
    assert not (skills / "build-a-site" / "assets" / "starter" / "node_modules").exists()

    graph = skills / "use-the-graph" / "scripts" / "graph.py"
    listing = subprocess.run(["python3", str(graph), "list"], env=env, capture_output=True, text=True, check=True).stdout
    assert "[pricing]" in listing and "[hero_compositions]" in listing
    stages = subprocess.run(["python3", str(graph), "stages"], env=env, capture_output=True, text=True, check=True).stdout
    assert "site_stage_sample" in stages
