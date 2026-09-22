#!/usr/bin/env bash
# Cut publishing-vN: the only way a publishing tag is made.
#
# A publishing tag has to contain the workflows it runs, and a reusable
# workflow cannot call a sibling by ./ path (that resolves against the
# consumer's repository -- .github#47). So the coordinator names its four
# siblings by full path at a literal tag, and this script is what keeps that
# literal equal to the tag being cut: it rewrites the refs, commits that one
# change, tags the commit, and pushes both. Run it on a clean main.
#
# Usage: scripts/cut_publishing_tag.sh N   (the number, e.g. 11)
set -euo pipefail
N="${1:?usage: cut_publishing_tag.sh N}"
[[ "$N" =~ ^[0-9]+$ ]] || { echo "N must be a number, got: $N" >&2; exit 1; }
TAG="publishing-v$N"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COORD="$ROOT/.github/workflows/reusable-publish-release-packages.yml"
cd "$ROOT"
[[ "$(git branch --show-current)" == "main" ]] || { echo "cut from main, not $(git branch --show-current)" >&2; exit 1; }
[[ -z "$(git status --porcelain)" ]] || { echo "working tree is not clean" >&2; exit 1; }
git fetch -q origin
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] || { echo "main is not level with origin/main" >&2; exit 1; }
git rev-parse -q --verify "refs/tags/$TAG" >/dev/null && { echo "$TAG already exists; tags are immutable, pick the next number" >&2; exit 1; }
if grep -nE '^\s*uses:\s*\./' .github/workflows/reusable-*.yml; then
    echo "a reusable calls a sibling by ./ path; fix that first (.github#47)" >&2; exit 1
fi
sed -i -E "s#(PyDevices/\.github/\.github/workflows/[a-z-]+\.yml@)publishing-v[0-9]+#\1$TAG#g" "$COORD"
refs=$(grep -oE 'workflows/[a-z-]+\.yml@publishing-v[0-9]+' "$COORD" | sort -u)
echo "$refs"
[[ "$(echo "$refs" | sed 's/.*@//' | sort -u | wc -l)" == "1" ]] || { echo "sibling refs disagree after rewrite" >&2; exit 1; }
if git diff --quiet; then
    echo "coordinator already names $TAG; tagging HEAD"
else
    git add "$COORD"
    git commit -qm "$TAG: the coordinator's sibling refs name their own tag"
fi
git tag -a "$TAG" -m "$TAG, cut by scripts/cut_publishing_tag.sh at $(git rev-parse --short HEAD)"
git push -q origin main "$TAG"
echo "cut $TAG at $(git rev-parse --short HEAD)"
