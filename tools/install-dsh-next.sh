#!/usr/bin/env bash
# Copy Theseus's skills and the current knowledge graph into a DSH NEXT home.
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
mkdir -p "$DEST/use-the-graph/references"
cp "$ROOT/knowledge/business-operating.grag.json" "$DEST/use-the-graph/references/"

echo "Installed into $DEST:"
for d in "$DEST"/*/; do echo "  $(basename "$d")"; done
python3 "$DEST/use-the-graph/scripts/graph.py" list | wc -l | awk '{print "  graph reachable: " $1 " topics"}'
