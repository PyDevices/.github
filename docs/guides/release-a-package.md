# Release a package

A published GitHub Release named `vX.Y.Z` is the release event. The tag picks
the exact files to build and `X.Y.Z` becomes the package version. A manual
workflow run only retries an existing tag; it never publishes an untagged
branch or a different commit.

The chain, from your side:

```text
Prepare release (workflow_dispatch, optional version)
  -> the workflow opens a release PR carrying VERSION + CHANGELOG.md
  -> you confirm or edit the version on that PR, then merge it
  -> Tag release creates the vX.Y.Z tag and GitHub Release
  -> Publish release packages: build -> TestPyPI -> files attached to the Release
     -> MIP index (final releases only) and library index -> health report
```

Choosing the version is the one step the automation leaves to you.

## 1. Dispatch "Prepare release"

```bash
gh workflow run prepare-release.yml --repo PyDevices/<repository>
# or with a version:
gh workflow run prepare-release.yml --repo PyDevices/<repository> -f version=X.Y.Z
```

The `version` input is a suggestion. Left empty, the workflow takes the
highest existing `vX.Y.Z` tag and adds one to the patch number. Neither that
value nor one you pass is committed until you confirm it on the pull request.
The workflow then:

1. Checks the version against `X.Y.Z[{a|b|rc}N|.devN]` and refuses a tag that
   exists.
2. Writes it to `VERSION` and puts a `## vX.Y.Z (date)` section at the top of
   `CHANGELOG.md`, built from `git log` since the last tag.
3. Opens or updates a pull request named `Release X.Y.Z` from the branch
   `release/vX.Y.Z`.

## 2. Review and merge the release PR

Confirm the version (push a commit to the branch to change `VERSION`), read
the changelog section, check that CI is green, and merge. Closing the pull
request without merging publishes nothing.

## 3. Tag release runs by itself

On every push to `main` that changes `VERSION`, the tag workflow creates the
`vX.Y.Z` tag and the GitHub Release at that commit. It marks the Release as a
pre-release when the version ends in `aN`, `bN`, `rcN` or `.devN`.

It uses a GitHub App token, not the default `GITHUB_TOKEN`, on purpose: a
Release created with `GITHUB_TOKEN` doesn't trigger `on: release` workflows,
so the publish run would never start.

If GitHub never delivered the push event for a merge, run the repository's tag
workflow by hand from `main`. A caller that also triggers on
`workflow_dispatch` and passes its `release` and `dry-run` inputs through (the
shape is in the header comment of
[`reusable-tag-on-release-merge.yml`](../../.github/workflows/reusable-tag-on-release-merge.yml))
tags the commit that brought `VERSION` to that version. Leave `release` blank
to tag `VERSION` as it stands, or give a version or the merge's SHA. Set
`dry-run` to see what it would tag.

## 4. Publish release packages runs on the Release

The publish workflow resolves and checks the tag, builds, uploads to TestPyPI,
attaches the built files to the Release, requests MIP and library-index
publication, and reports to the [Release Health
dashboard](../how-it-works/release-chain.md#the-release-health-dashboard)
whatever the outcome. A final release can also go to production PyPI; see
[publish to production PyPI](publish-to-pypi.md). Each job is described in
[the release chain](../how-it-works/release-chain.md).

## The manual fallback

A release pull request is the default, but a hand-made tag and Release are valid
for a hotfix or a recovery. The one rule: the tag and the committed `VERSION`
must match exactly, because the build jobs reject a mismatch.

```bash
git switch main && git pull --ff-only
version=X.Y.Z
printf '%s\n' "$version" > VERSION
git add VERSION CHANGELOG.md
git commit -m "Release ${version}"
git push origin main

gh release create "v${version}" \
  --repo PyDevices/<repository> \
  --target "$(git rev-parse HEAD)" \
  --title "v${version}" \
  --generate-notes
```

`gh release create` with your own token starts the publish run normally, and
publishes immediately unless you pass `--draft`. In the GitHub web UI, choose
the exact version commit, create `vX.Y.Z` and press **Publish release**:
pushing a tag, or saving a draft, doesn't start the publish run.

## Retry an interrupted publication

Never move the tag or rebuild a version from a different commit. Run the
publish workflow again with the existing tag:

```bash
gh workflow run publish-release-packages.yml \
  --repo PyDevices/<repository> \
  -f release-ref=vX.Y.Z
```

The workflow checks out that tag and validates it again, and TestPyPI uploads
use `skip-existing: true`, so a partial upload completes without replacing
files TestPyPI already took.

If only the MIP run or its Pages deployment failed, rerun its failed jobs:

```bash
gh run rerun <mip-run-id> --repo PyDevices/mip --failed
```

A rerun can stay pinned to the reusable-workflow commit the first attempt
used. If the reusable's ref changed since, start a new exact-tag retry from the
source repository, or dispatch the MIP queue by hand:

```bash
gh workflow run process-mip-publication-request.yml \
  --repo PyDevices/mip \
  -f source-repository=PyDevices/<repository> \
  -f source-ref=vX.Y.Z \
  -f version=X.Y.Z \
  -f profile=<palettes|pdwidgets|pygraphics|pydevices|audioinstruments|audioeffects>
```

Dispatch the queue directly only to recover, after you've confirmed the tag
and the profile. A repository's own release is the normal way in.

## Correct a bad release

Published TestPyPI files and released tags are immutable in practice. Deleting
a GitHub Release doesn't remove registry files, and moving a tag would make
the release impossible to reproduce.

1. Fix the source on `main`.
2. Run "Prepare release" again for a new version.
3. Repeat the flow above.
4. Yank an unusable TestPyPI version only when you must, and say why. Don't
   upload replacement files under the same version.

Publishing the corrected version replaces the package's `latest` entry in the
MIP index. To pull a bad release back sooner, see
[roll back a release](roll-back-a-release.md).
