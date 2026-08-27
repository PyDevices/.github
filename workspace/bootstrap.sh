#!/usr/bin/env bash
# Bootstrap the PyDevices multi-repository workspace from workspace/repos.json.
#
# Clones every active repository as a sibling of this .github checkout (or
# under $PYDEVICES_ROOT), fetching those already present. Full clones on
# purpose: the modernization program reads history (scenario S3). Idempotent;
# safe to run at the start of every session. Works the same in a Claude cloud
# session, a devcontainer, or a local checkout — one definition, all consumers.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${PYDEVICES_ROOT:-$(dirname "$(dirname "$SCRIPT_DIR")")}"
MANIFEST="$SCRIPT_DIR/repos.json"

python3 - "$MANIFEST" <<'PY' | while IFS=$'\t' read -r name local_dir status; do
import json, sys
m = json.load(open(sys.argv[1]))
for r in m["repos"]:
    print(f'{r["name"]}\t{r.get("local", r["name"])}\t{r["status"]}')
PY
    dest="$ROOT/$local_dir"
    if [ "$status" != "active" ]; then
        printf 'skip   %-22s (%s)\n' "$name" "$status"
        continue
    fi
    if [ -d "$dest/.git" ]; then
        printf 'fetch  %-22s\n' "$name"
        git -C "$dest" fetch --quiet --all --prune </dev/null || printf 'WARN   %-22s fetch failed\n' "$name"
    else
        printf 'clone  %-22s -> %s\n' "$name" "$dest"
        git clone --quiet "https://github.com/PyDevices/$name.git" "$dest" </dev/null \
            || printf 'WARN   %-22s clone failed (no access? not published?)\n' "$name"
    fi
done
echo "workspace root: $ROOT"
