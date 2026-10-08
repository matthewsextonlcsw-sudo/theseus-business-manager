"""Integration test: the Standard-tier starter builds, and QA judges it correctly.

With placeholders, QA must fail on placeholder text. With the fictional example (a regulated dental
practice), QA must pass everything except the reserved 555 phone number.
Needs Node, the starter's node_modules and agent-browser; skipped otherwise.
"""
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
STARTER = ROOT / "starter"
QA = ROOT / "skills" / "build-a-site" / "scripts" / "qa.sh"
WRAPPER = ROOT / "skills" / "browse-like-a-person" / "scripts" / "browser"

pytestmark = pytest.mark.skipif(
    shutil.which("agent-browser") is None or not (STARTER / "node_modules").is_dir(),
    reason="needs agent-browser and starter/node_modules (run npm install in starter/)",
)


def _copy_starter(target: Path) -> None:
    """Copy the starter, skipping only its own top-level build output (not packages' dist folders)."""
    top = str(STARTER)
    shutil.copytree(STARTER, target, symlinks=True, ignore=lambda d, names: [n for n in names if d == top and n in ("dist", ".astro")])


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _build_and_qa(project: Path, tmp_path: Path, regulated: bool) -> subprocess.CompletedProcess:
    subprocess.run(["npm", "run", "build"], cwd=project, check=True, capture_output=True, timeout=300)
    port = _free_port()
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "--directory", str(project / "dist")],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    env = dict(
        os.environ,
        THESEUS_BROWSER_HOME=str(tmp_path / "browser"),
        THESEUS_BROWSER_HEADED="0",
        AGENT_BROWSER_SESSION="starter-test",
        QA_REGULATED="1" if regulated else "0",
    )
    try:
        return subprocess.run(
            ["bash", str(QA), f"http://127.0.0.1:{port}/", str(tmp_path / "qa")],
            capture_output=True, text=True, env=env, timeout=300,
        )
    finally:
        server.terminate()
        subprocess.run([str(WRAPPER), "close"], capture_output=True, env=env, timeout=60)


def test_placeholders_fail_qa(tmp_path: Path) -> None:
    project = tmp_path / "site"
    _copy_starter(project)
    result = _build_and_qa(project, tmp_path, regulated=False)
    assert result.returncode == 1, result.stdout
    assert "FAIL  no placeholder text (/\\[insert/i)" in result.stdout


def test_filled_example_passes_everything_but_the_fictional_phone(tmp_path: Path) -> None:
    project = tmp_path / "site"
    _copy_starter(project)
    shutil.copy(project / "examples" / "site.example.ts", project / "src" / "data" / "site.ts")
    result = _build_and_qa(project, tmp_path, regulated=True)
    failures = [line for line in result.stdout.splitlines() if line.startswith("FAIL")]
    assert failures == ["FAIL  no placeholder text (/\\b555-\\d{4}\\b/)"], result.stdout
    assert "ok    accessibility: 0 violations" in result.stdout
    assert "ok    crisis notice with 988 is on the page" in result.stdout
