#!/usr/bin/env python3
"""Install a hand-picked set of ECC skills into a DSH NEXT home.

ECC (https://github.com/affaan-m/ECC, MIT license) is a large open skill library. Theseus uses
nine of its skills that are small, harness-neutral and fit a small studio. They are downloaded
at one pinned ECC commit, so updates happen only when ECC_COMMIT is changed on purpose.
Copies are not kept in this repo.

Usage: python3 tools/install_ecc_skills.py          (DSH_HOME defaults to ~/.dsh-next)
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ECC_REPO = "affaan-m/ECC"
ECC_COMMIT = "ef648e01899ba3e8dc6371642deaaf64b4477775"
SKILLS = (
    "hipaa-compliance",
    "healthcare-phi-compliance",
    "seo",
    "design-system",
    "frontend-a11y",
    "email-ops",
    "market-research",
    "brand-voice",
    "agent-self-evaluation",
)
TIMEOUT = 30


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "theseus-business-manager"})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read()


def select_paths(tree: list[dict], skills: tuple[str, ...]) -> dict[str, list[str]]:
    """Map each chosen skill to the blob paths inside its folder."""
    chosen: dict[str, list[str]] = {name: [] for name in skills}
    for entry in tree:
        if entry.get("type") != "blob":
            continue
        parts = entry["path"].split("/")
        if len(parts) >= 3 and parts[0] == "skills" and parts[1] in chosen:
            chosen[parts[1]].append(entry["path"])
    return chosen


def install(dest_root: Path) -> int:
    tree_url = f"https://api.github.com/repos/{ECC_REPO}/git/trees/{ECC_COMMIT}?recursive=1"
    tree = json.loads(fetch(tree_url))["tree"]
    chosen = select_paths(tree, SKILLS)
    missing = [name for name, paths in chosen.items() if not any(p.endswith("/SKILL.md") for p in paths)]
    if missing:
        print(f"Not found at {ECC_COMMIT[:7]}: {', '.join(missing)}", file=sys.stderr)
        return 1

    raw = f"https://raw.githubusercontent.com/{ECC_REPO}/{ECC_COMMIT}/"
    license_text = fetch(raw + "LICENSE")
    for name, paths in chosen.items():
        target = dest_root / name
        for path in paths:
            relative = Path(*path.split("/")[2:])
            out = target / relative
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(fetch(raw + path))
        (target / "LICENSE.ECC").write_bytes(license_text)
        (target / "SOURCE.md").write_text(
            f"From ECC ({ECC_REPO}) at commit {ECC_COMMIT}, MIT license (see LICENSE.ECC).\n"
            "Installed by theseus-business-manager/tools/install_ecc_skills.py.\n",
            encoding="utf-8",
        )
        print(f"  {name} ({len(paths)} files)")
    print(f"Installed {len(chosen)} ECC skills at {ECC_COMMIT[:7]} into {dest_root}")
    return 0


if __name__ == "__main__":
    home = Path(os.environ.get("DSH_HOME", Path.home() / ".dsh-next")).expanduser()
    sys.exit(install(home / "skills"))
