"""Integration test: build-a-site's qa.sh must fail a deliberately bad page.

Needs agent-browser and a display; skipped when agent-browser is not installed.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / "skills" / "build-a-site" / "scripts" / "qa.sh"
BAD = ROOT / "tests" / "fixtures" / "bad-site" / "index.html"

pytestmark = pytest.mark.skipif(shutil.which("agent-browser") is None, reason="agent-browser not installed")


def test_bad_page_fails_with_the_planted_problems(tmp_path: Path) -> None:
    # Own profile and own session, so the test never touches the agent's running browser.
    env = dict(
        os.environ,
        QA_REGULATED="1",
        THESEUS_BROWSER_HOME=str(tmp_path / "browser"),
        THESEUS_BROWSER_HEADED="0",
        AGENT_BROWSER_SESSION="qa-test",
    )
    result = subprocess.run(
        ["bash", str(QA), BAD.as_uri(), str(tmp_path / "qa")],
        capture_output=True, text=True, env=env, timeout=240,
    )
    wrapper = ROOT / "skills" / "browse-like-a-person" / "scripts" / "browser"
    subprocess.run([str(wrapper), "close"], capture_output=True, env=env, timeout=60)
    report = result.stdout
    assert result.returncode == 1, report
    for expected in (
        "FAIL  sideways scroll at phone width",
        "FAIL  every image has alt text",
        "FAIL  every form field has a label",
        "FAIL  no placeholder text",
        "FAIL  no form fields asking for health details",
        "FAIL  crisis notice with 988 is on the page",
        "FAIL  page declares its language",
    ):
        assert expected in report, f"missing: {expected}\n{report}"
