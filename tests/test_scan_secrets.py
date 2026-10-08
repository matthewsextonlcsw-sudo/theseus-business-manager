"""The pre-push secret scanner: blocks keys and private addresses, exempts only the private link's fixed /30.

Test addresses and keys are built at run time, so this file never holds a string the scanner would block.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

SCANNER = Path(__file__).resolve().parents[1] / "tools" / "scan-secrets.sh"


def ip(*parts: int) -> str:
    return ".".join(str(p) for p in parts)


def scan(tmp_path: Path, files: dict[str, str]) -> subprocess.CompletedProcess[str]:
    repo = tmp_path / "repo"
    (repo / "tools").mkdir(parents=True)
    shutil.copy(SCANNER, repo / "tools" / "scan-secrets.sh")
    for name, text in files.items():
        (repo / name).write_text(text)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    return subprocess.run(["bash", "tools/scan-secrets.sh"], cwd=repo, capture_output=True, text=True)


def test_the_private_links_fixed_addresses_pass(tmp_path: Path) -> None:
    text = f"BRAIN_URL=http://{ip(10, 77, 0, 1)}:8096/v1 and peer {ip(10, 77, 0, 2)}/32\n"
    result = scan(tmp_path, {"README.md": text})
    assert result.returncode == 0, result.stdout


def test_other_private_addresses_are_still_blocked(tmp_path: Path) -> None:
    for address in (ip(10, 0, 0, 5), ip(10, 77, 0, 4), ip(10, 77, 1, 1), ip(192, 168, 0, 10), ip(172, 16, 0, 9), ip(100, 64, 1, 2)):
        result = scan(tmp_path / address, {"notes.md": f"server at {address}\n"})
        assert result.returncode == 1 and "BLOCK" in result.stdout, address


def test_a_real_address_next_to_an_exempt_one_is_still_caught(tmp_path: Path) -> None:
    result = scan(tmp_path, {"notes.md": f"link {ip(10, 77, 0, 1)}, home {ip(10, 0, 0, 5)}\n"})
    assert result.returncode == 1


def test_key_shaped_strings_are_blocked(tmp_path: Path) -> None:
    result = scan(tmp_path, {"config.md": "token = " + "sk" + "-" + "a" * 24 + "\n"})
    assert result.returncode == 1
