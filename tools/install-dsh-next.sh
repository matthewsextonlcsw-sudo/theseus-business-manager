#!/usr/bin/env bash
# Copy Theseus's skills and the active knowledge graphs into a DSH NEXT home.
# Usage: bash tools/install-dsh-next.sh            (installs into $DSH_HOME, default ~/.dsh-next)
# Copies instead of symlinking, so the harness never needs access to this repo's folder.
# Existing files are overwritten; nothing is deleted.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DSH_HOME="${DSH_HOME:-$HOME/.dsh-next}"
DEST="$DSH_HOME/skills"

mkdir -p "$DEST"
for skill in "$ROOT"/skills/*/; do
  [ -f "$skill/SKILL.md" ] || continue
  name="$(basename "$skill")"
  mkdir -p "$DEST/$name"
  cp -R "$skill". "$DEST/$name/"
done
# Every active graph (business and website craft); archived versions (*.v1.*) stay in the repo.
mkdir -p "$DEST/use-the-graph/references"
for graph in "$ROOT"/knowledge/*.grag.json; do
  case "$(basename "$graph")" in *.v1.*) continue ;; esac
  cp "$graph" "$DEST/use-the-graph/references/"
done
# The website craft playbook travels with build-a-site, for reading in full.
if [ -d "$DEST/build-a-site" ] && [ -f "$ROOT/knowledge/website-craft.md" ]; then
  mkdir -p "$DEST/build-a-site/references"
  cp "$ROOT/knowledge/website-craft.md" "$DEST/build-a-site/references/"
fi

# The Standard-tier starter travels with build-a-site (source only, no installed packages or builds).
if [ -d "$ROOT/starter" ] && [ -d "$DEST/build-a-site" ]; then
  mkdir -p "$DEST/build-a-site/assets"
  rsync -a --exclude node_modules --exclude dist --exclude .astro "$ROOT/starter/" "$DEST/build-a-site/assets/starter/"
fi

echo "Installed into $DEST:"
for d in "$DEST"/*/; do echo "  $(basename "$d")"; done
python3 "$DEST/use-the-graph/scripts/graph.py" list | wc -l | awk '{print "  graph reachable: " $1 " topics"}'
