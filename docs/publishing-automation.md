# Releasing and publishing PyDevices packages

This is the organization-wide runbook for publishing a new package version, and
it **lives here because it is org-wide**: it governs `palettes`, `pdwidgets`,
`pygraphics`, `pydevices`, and `lvgl-python`, and it documents the reusable
workflows and shared secrets that this repository owns.

Repository-specific publishing documents cover only what their own release
produces — for example
[pydevices/docs/publishing.md](https://github.com/PyDevices/pydevices/blob/main/docs/publishing.md)
describes that repo's dynamically discovered package set. They add build or test
details; they do not restate or replace the procedure below.

A **published GitHub Release named `vX.Y.Z` is the authoritative release
event**. The source tag selects the exact files to build, and `X.Y.Z` becomes
the package version. A manual workflow run is only a retry of an existing
exact tag; it is not a way to publish an untagged branch or a different commit.

## What each repository publishes

| Source repository | TestPyPI | PyDevices MIP index |
|---|---|---|
| `palettes` | `pydevices-palettes` wheel and sdist | `palettes` |
| `pdwidgets` | `pydevices-pdwidgets` wheel and sdist | `pdwidgets` |
| `pygraphics` | `pydevices-pygraphics` Linux, Windows, Android, and PyEmscripten wheels | Pure-Python `pygraphics` |
| `pydevices` | `pydevices` (all of `lib/`) and `pydevices-desktop` | One package per `lib/` component, plus `pydevices` and `pydevices-desktop` |
| `lvgl-python` | `pydevices-lvgl` Linux, Windows, Android, and PyEmscripten wheels | Nothing |

The pip distribution names are prefixed with `pydevices-`; MIP package names
are not. `pydevices` and `pydevices-desktop` keep the same name in both
systems.

### The dynamic `pydevices` release

The `pydevices` build does not maintain an inclusion list. **The distribution
is exactly `lib/`, nothing more** — but the two ecosystems package it
differently, because their constraints differ:

- **Both ecosystems ship `lib/` as a single package.** On PyPI that is the
  `pydevices` distribution; on MIP the `pydevices` package.
- Publishing a package per component was tried and dropped. micropython-lib
  resolves `require()` by **inclusion at build time**, not as a dependency
  edge, so the index materialised every required component's files into each
  package that required it -- `displaydev` and `appdev` each carried their own
  copy of `events.py`, and installing both wrote it twice. The granularity was
  an illusion, and it cost a package per component to maintain.
- The trade is real but bounded: a display-only board installs about 232 KiB
  more source than `displaydev` alone used to pull. Revisit if that starts to
  matter on a target.
- Every publishable entry under `utils/`, plus everything publishable in
  `board_configs/desktop/`, is bundled into `pydevices-desktop`.
- `pydevices-desktop` depends on `pydevices`, so one install gets the complete
  desktop runtime.
- All artifacts from one `pydevices` release share a version.
- MIP meta-package dependencies resolve `latest` from the latest-only index.
- Only `pydevices` and `pydevices-desktop` declare `pypi_publish`; the MIP leaf
  packages deliberately do not, because they have no PyPI distribution of their
  own.
- Board `package.json` installers are not copied into the central MIP index.
  Install them from their documented raw GitHub paths; the desktop board
  runtime files themselves remain part of `pydevices-desktop`.

Adding or removing a publishable entry under `lib/` or `utils/` therefore
changes the next release automatically. Review the generated package set as
part of release preparation. Committed root TOML files (such as `pydevices-desktop.toml`
and `pydevices-examples.toml`) are PyScript filesystem mappings of the repository
payloads, not package metadata; their CI validation must pass before release.

## Automation and credentials

Each source repository has one coordinator:

```text
.github/workflows/publish-release-packages.yml
```

It validates `vX.Y.Z`, calls reusable workflows from
`PyDevices/.github@publishing-v1`, publishes validated artifacts, and, where
applicable, requests a serialized MIP update.

The following GitHub Actions secrets must already exist:

| Secret | Where needed | Purpose |
|---|---|---|
| `TESTPYPI_API_TOKEN` | Every repository that uploads to TestPyPI | API token currently owned by the `bdbarnett` TestPyPI account |
| `MICROPYTHON_LIB_DEPLOY_TOKEN` | Source repositories that publish MIP packages, and `PyDevices/mip` | Dispatch the MIP request and commit the resulting index update |
| `RELEASE_WORKFLOW_TOKEN` | **`lvgl-python` only** (`sync-and-release.yml`) | Create the GitHub Release. Not redundant with `GITHUB_TOKEN`: a Release created with `GITHUB_TOKEN` does **not** trigger `on: release` workflows, so publishing would silently never run. |
| `LVCPYTHON_MOD_DISPATCH_TOKEN` | **`lvgl-bindings` only** (`trigger-lvgl-python-release.yml`, `check-dispatch-token.yml`) | Dispatch `lvgl-python`'s sync workflow across repositories |
| `VSCE_PAT`, `OVSX_PAT` | **`mpftp` only** (`publish-vsix.yml`) | VS Marketplace and Open VSX. Both optional; the steps skip when unset |

TestPyPI currently uses token authentication while the PyDevices TestPyPI
organization request is pending. The upload action must receive:

```yaml
user: __token__
password: ${{ secrets.TESTPYPI_API_TOKEN }}
repository-url: https://test.pypi.org/legacy/
skip-existing: true
```

This is different from Trusted Publishing. OIDC publishing requires a
matching TestPyPI Trusted Publisher for the organization, repository,
workflow, and optional environment. Do not add `id-token: write` or remove the
password until the PyDevices organization and its Trusted Publishers have
actually been configured.

Before every release, confirm that the coordinator still references the
intended stable shared-workflow ref and that the required secrets are present.
Do not move or replace a stable publishing ref as part of an ordinary package
release.

## Planned: real MIP dependencies instead of `require()` inclusion

**Not started.** Cross-repository `require()`s were removed in the meantime, so
MIP packages currently have **no** dependencies at all — see "Current state"
below.

### The finding

`mip`'s package format supports install-time dependencies, and the client
resolves them. `utils/mip.py` walks `package_json["deps"]` and recursively
installs each entry, which is how board-config `package.json` files work
(`"deps": [["pydevices", "latest"]]`).

`build.py` never emits that field. The string `deps` appears in it exactly
once, in a comment on the format:

```
#   "deps": [   <-- not used by micropython-lib packages
```

`require()` in a `manifest.py` is a **build-time include**, inherited from the
manifest system used to freeze modules into firmware. It folds the required
package's files into the requiring package and emits one flat file list.

So the three layers disagree: the format supports deps, the client resolves
deps, the builder never writes them.

### What that produced

Before removal, `pdwidgets` required `pydevices`, `pygraphics`, and `palettes`
— and its index entry was **212 files with `deps: null`**, carrying a complete
copy of all three. A board installing `pdwidgets` and `pydevices` wrote every
`lib/` file twice, and `pdwidgets` could not be updated without re-fetching
everything it had absorbed.

### Two ways to fix it

| Approach | Scope | Cost |
|---|---|---|
| **Patch `build.py`** so `require()` emits a `deps` entry rather than inlining | The whole index | Changes behaviour for the ~25 inherited upstream packages too — `aioble` and friends require each other — and is a permanent fork divergence to carry against upstream |
| **Emit hand-written `package.json`** for PyDevices packages, as board configs already do, bypassing the manifest path | PyDevices packages only | Leaves upstream untouched, but means maintaining a second publishing path alongside `synchronize_mip_package.py` |

The second is narrower and does not touch inherited files, which
[repo-layout.md](repo-layout.md) protects. The first is more honest if the
index is to behave like a package index generally.

Either way, verify against a real device install before switching: `deps`
resolution is client-side, so an older `mip` on a board may not honour it.

### Current state

Cross-repository `require()`s are removed from every profile. Consequences:

- **MIP:** `mip.install("pdwidgets")` installs *only* `pdwidgets`. Its
  dependencies must be installed by hand — the README and `docs/index.md` now
  say so explicitly.
- **pip:** unaffected. `pdwidgets/pyproject.toml` keeps real dependencies and
  pip resolves them normally.
- `pydevices-desktop` still requires `pydevices`. That one is intra-repository
  — both are generated from the same source tree — so it is inclusion of code
  that ships together anyway, not another repo's package.

## Planned: type stubs for every published package

**Not started. Recorded so the reasoning is not re-derived.**

Intent: ship `.pyi` stubs for all published packages so pip consumers get real
type information.

### Why stubs rather than annotations

These packages run on MicroPython, where annotations cost bytecode and RAM.
That is why the convention is types in docstrings, not signatures. A `.pyi`
file carries the same information for a type checker, costs nothing at
runtime, and never reaches a device — MIP installs `.py` files only, verified
against the live index.

The org already does this elsewhere: `lvgl-bindings` generates `lvgl.pyi` and
syncs it into `lvgl-python`, and `pydevices-examples/tools/typings/` holds a
tree of `.pyi` for MicroPython builtins.

### The `py.typed` constraint

Maintainer preference is **no `py.typed` files**. PEP 561 makes that a real
constraint rather than a formatting choice: a type checker ignores `.pyi`
bundled inside a regular package unless `py.typed` is present. Stubs dropped
into the `pydevices` wheel without the marker would ship and never be read.

Two mechanisms avoid the marker:

| Mechanism | pip-installable | Needs `py.typed` |
|---|---|---|
| **GitHub Release assets** — `.pyi` attached per tag, consumer points `mypy_path` / `stubPath` at them | no, manual setup | no — not a distribution |
| **A `pydevices-stubs` distribution** — importable dirs named `multimer-stubs/`, `displaydev-stubs/`, … | yes | no — PEP 561 exempts stub-only packages |

Maintainer picked release assets when asked. The `-stubs` route was surfaced
afterwards and satisfies both constraints more completely; decide between them
before starting.

### Scope

Roughly 633 functions across `appdev`, `audiodev`, `displaydev`, and
`multimer`. `stubgen` (mypy) is the starting point, but on unannotated source
it emits mostly `Any`, which is worth nothing to a consumer — the work is
hand-writing signatures. Treat generation as scaffolding, not output.

`displaydev` is partly annotated already (101 of 310 functions), clustered in
the host backends — `sdldisplay` 19/42, `pgdisplay` 17/33 — while MCU-facing
files such as `windisplay` are at 0/27. Those inline annotations are a
reasonable seed for its stubs, and `busdisplay` at 16/26 is worth a look on
its own, since that is MCU code carrying a cost the convention says it should
not.

### What prompted this

`lib/multimer/py.typed` was removed in the 0.1.4 cycle. It claimed the package
shipped inline types while annotating 0 of 151 functions, which makes checker
inference strictly worse than no marker: `py.typed` tells a checker to trust
inline types and stop looking for stubs.

## How the release chain is wired

Each publishing repository has a ~26-line `publish-release-packages.yml` that
calls one reusable workflow and supplies only what differs — the build kind, the
distribution name, and the MIP profile:

```yaml
jobs:
  publish:
    uses: PyDevices/.github/.github/workflows/reusable-publish-release-packages.yml@publishing-v2
    with:
      build-kind: pure-python          # or native-and-wasm, pydevices-multi
      distribution-name: pydevices-palettes
      import-name: palettes
      mip-profile: palettes            # omit to skip MIP, as lvgl-python does
      release-ref: ${{ inputs.release-ref }}
    secrets: inherit
```

That reusable resolves and validates the `vX.Y.Z` tag, runs the matching build,
uploads to TestPyPI, and requests MIP publication. It replaced five copies of
the same three jobs.

**Callers pin `@publishing-v2`.** `publishing-v1` is left in place so a release
cut before the consolidation can still be retried against the contract it was
built with.

## Standard release procedure

The commands below assume sibling repositories under your PyDevices
workspace root (for example `~/gh/pydevices`). Substitute the repository
and version being released.

### 1. Start from synchronized `main`

```bash
cd <workspace-root>/<repository>
git switch main
git fetch origin --prune
git pull --ff-only
git status --short
```

The worktree must be clean. Confirm that all changes intended for the release
are committed and that required CI checks pass. Follow the source repository's
test instructions; native repositories may require substantially more build
validation than pure-Python repositories.

### 2. Choose a new version

Use a version that has never been published for that distribution. TestPyPI
files are immutable, and an uploaded filename cannot be replaced.

```bash
version=X.Y.Z
tag="v${version}"

git tag --list "$tag"
gh release view "$tag" --repo PyDevices/<repository>
```

Both commands should report that the proposed release does not exist. Also
check the TestPyPI project page when there is any doubt about previously
uploaded versions.

### 3. Commit the version

For `palettes`, `pdwidgets`, `pygraphics`, and `pydevices`, write the exact
version to the repository's `VERSION` file and commit it with the release
changes:

```bash
printf '%s\n' "$version" > VERSION
git diff --check
git diff -- VERSION

# Run the repository's tests here.

git add VERSION <other-release-files>
git commit -m "Release ${version}"
git push origin main
```

Do not create the release until the version commit is on `origin/main` and CI
has passed. The build workflows reject a tag whose `X.Y.Z` does not match the
committed `VERSION`.

`pydevices` uses this one `VERSION` value for every discovered leaf, both meta
packages, and both publishing channels. Do not assign separate component
versions.

### 4. Publish the GitHub Release

Record the exact commit before creating the release so a later push cannot
change the intended target:

```bash
release_commit="$(git rev-parse HEAD)"
test "$release_commit" = "$(git rev-parse origin/main)"

gh release create "$tag" \
  --repo PyDevices/<repository> \
  --target "$release_commit" \
  --title "$tag" \
  --generate-notes
```

`gh release create` publishes immediately unless `--draft` is supplied. If a
release is prepared in the GitHub web UI, select the exact version commit,
create `vX.Y.Z`, and **Publish release**. Merely pushing a tag or saving a draft
does not trigger the package coordinator.

Verify the release target:

```bash
gh release view "$tag" \
  --repo PyDevices/<repository> \
  --json isDraft,isPrerelease,tagName,targetCommitish,url
```

### 5. Monitor the source publication

Find and watch the run started by the release event:

```bash
gh run list \
  --repo PyDevices/<repository> \
  --workflow publish-release-packages.yml \
  --limit 5

gh run watch <run-id> \
  --repo PyDevices/<repository> \
  --exit-status
```

A successful source run means:

1. The tag and committed version matched.
2. All distributions or wheels built successfully.
3. The complete artifact set passed package and filename validation.
4. TestPyPI accepted the API-token upload, when the repository has a pip
   product.
5. The MIP request was dispatched, when the repository has a MIP product.

The TestPyPI upload and MIP dispatch can run in parallel after the build. A
successful source run means the MIP request was accepted, not necessarily that
the central queue and Pages deployment have finished.

### 6. Monitor the central MIP queue

Skip this step for `lvgl-python`.

```bash
gh run list \
  --repo PyDevices/mip \
  --workflow process-mip-publication-request.yml \
  --limit 10

gh run watch <mip-run-id> \
  --repo PyDevices/mip \
  --exit-status
```

`PyDevices/mip` serializes requests so concurrent source releases cannot
overwrite one another. For each request it:

1. Checks out the exact source tag.
2. Regenerates that repository's MIP packages.
3. Removes temporary publishing checkouts before index validation.
4. Validates and compiles the complete latest-only index.
5. Creates one atomic bot commit under `micropython/` when content changed.
6. Builds and deploys the complete GitHub Pages artifact to
   `https://PyDevices.github.io/mip`.

Wait for both the synchronization job and `deploy-complete-mip-index` to
succeed.

### 7. Verify the registries

Check the exact TestPyPI version, not only the workflow status:

```bash
python - <<'PY'
import json
import urllib.request

project = "<testpypi-project>"
version = "X.Y.Z"
with urllib.request.urlopen(
    f"https://test.pypi.org/pypi/{project}/json", timeout=30
) as response:
    data = json.load(response)
files = data["releases"].get(version, [])
if not files:
    raise SystemExit(f"{project} {version} is not published")
print(f"{project} {version}: {len(files)} published files")
PY
```

For native projects, inspect the returned filenames or the TestPyPI Files tab
and confirm the expected Linux, Windows, Android, and PyEmscripten wheel set.
For `pydevices`, verify every discovered leaf plus `pydevices` and
`pydevices-desktop`, all at the same version.

Check the live MIP index after Pages deployment:

```bash
python - <<'PY'
import json
import urllib.request

package = "<mip-package>"
version = "X.Y.Z"
with urllib.request.urlopen(
    "https://PyDevices.github.io/mip/index.json", timeout=30
) as response:
    index = json.load(response)
matches = [entry for entry in index["packages"] if entry["name"] == package]
if not matches or matches[0]["version"] != version:
    raise SystemExit(f"{package} {version} is not live")
print(f"{package} {version} is live")
PY
```

Finally, retain the GitHub Release URL and both Actions run URLs in the release
record or handoff.

## LVGL release procedure

`lvgl-python` normally receives generated bindings from `lvgl-bindings`; its
version is not chosen with the generic `VERSION` edit above. The preferred
flow is:

```text
lvgl-bindings generated-source change
  -> Trigger lvgl-python release
  -> lvgl-python Sync and release
  -> write VERSION, commit main, publish vX.Y.Z
  -> Publish release packages
  -> build and upload the complete pydevices-lvgl wheel matrix
```

Start the sync explicitly when needed:

```bash
gh workflow run sync-and-release.yml --repo PyDevices/lvgl-python
```

Or select an exact `lvgl-bindings` ref:

```bash
gh workflow run sync-and-release.yml \
  --repo PyDevices/lvgl-python \
  -f lvgl_bindings_ref=<commit-or-tag>
```

The workflow derives the LVGL major/minor line and increments this repository's
release counter, writes `VERSION`, commits, and publishes the GitHub Release.
Then monitor `publish-release-packages.yml` and verify TestPyPI as described
above. `lvgl-python` does not dispatch a MIP publication.

Use `skip_publish=true` only to synchronize and commit without creating a
release:

```bash
gh workflow run sync-and-release.yml \
  --repo PyDevices/lvgl-python \
  -f skip_publish=true
```

The detailed LVGL version derivation and local reproduction steps remain in
`lvgl-python/docs/publishing.md`.

## Retrying an interrupted publication

Never move the tag or rebuild the same version from a different commit. Retry
the coordinator with the exact existing tag:

```bash
gh workflow run publish-release-packages.yml \
  --repo PyDevices/<repository> \
  -f release-ref=vX.Y.Z

gh run list \
  --repo PyDevices/<repository> \
  --workflow publish-release-packages.yml \
  --limit 5
```

The workflows check out that tag, revalidate it, and use `skip-existing: true`
for TestPyPI. This safely completes a partial upload without replacing files
that TestPyPI already accepted.

If only the current MIP run or Pages deployment failed, retry its failed jobs:

```bash
gh run rerun <mip-run-id> --repo PyDevices/mip --failed
gh run watch <mip-run-id> --repo PyDevices/mip --exit-status
```

If the shared reusable-workflow ref changed after the failed run, GitHub's
**rerun** operation may remain pinned to the reusable workflow commit selected
by the original attempt. Start a fresh source exact-tag retry, or dispatch a
fresh central MIP run:

```bash
gh workflow run process-mip-publication-request.yml \
  --repo PyDevices/mip \
  -f source-repository=PyDevices/<repository> \
  -f source-ref=vX.Y.Z \
  -f version=X.Y.Z \
  -f profile=<palettes|pdwidgets|pygraphics|pydevices>
```

Use a direct central dispatch only for recovery after confirming that the
source tag and profile are correct. The normal entry point is always the
source repository's release coordinator.

## Correcting a bad release

Published TestPyPI files and released source tags are immutable in practice.
Deleting a GitHub Release does not remove registry files, and moving a tag
would make the release irreproducible.

To correct a release:

1. Fix the source on `main`.
2. Choose a new version.
3. Repeat the complete standard release procedure.
4. Yank an unusable TestPyPI version only when necessary and document why; do
   not attempt to upload replacement files under the same version.

Publishing the corrected MIP version replaces the affected package's `latest`
entry when the central latest-only index is deployed.

## Troubleshooting

| Symptom | Meaning and response |
|---|---|
| No publication run after pushing a tag | A tag alone is not the trigger. Publish the GitHub Release. |
| `VERSION contains ... but the release tag is ...` | Fix and commit `VERSION`, then create a **new** tag/version. Do not move a published tag. |
| TestPyPI `invalid-publisher` | The job attempted OIDC Trusted Publishing without a matching publisher. The current contract must use `__token__` and `TESTPYPI_API_TOKEN`. |
| TestPyPI authentication failure | Confirm that `TESTPYPI_API_TOKEN` exists in that source repository, belongs to `bdbarnett`, has permission for the project, and has not expired or been revoked. |
| TestPyPI duplicate-file response | Retry with the current coordinator, which sets `skip-existing: true`; otherwise publish a new version. |
| MIP request is queued | This is expected. The central concurrency group processes publication requests serially. |
| MIP validation sees `.publication-source/manifest.py` | The shared synchronization job is stale and did not remove temporary checkouts. Start a fresh run that resolves the current stable shared workflow. |
| Pages setup or action download returns 429/503/504 | This is usually transient GitHub infrastructure trouble. Retry the failed MIP job and verify the live index afterward. |
| Source workflow succeeds but MIP is still old | Inspect the downstream `PyDevices/mip` run and wait for the Pages deployment; source success only confirms dispatch. |
| A native wheel platform is missing | Fix the wheel matrix and publish a new version. TestPyPI cannot accept a replacement with an existing filename. |

## Shared implementation reference

For the workflows *outside* this release chain — the Pages `deploy.yml` pipeline,
test and lint jobs, validators, and the MIP index jobs — see
[workflows.md](workflows.md).

| Workflow | Responsibility |
|---|---|
| `reusable-build-pure-python-distribution.yml` | Build, check, clean-install, and upload one wheel/sdist artifact |
| `reusable-build-native-and-wasm-wheels.yml` | Build Linux, Windows, Android, and PyEmscripten wheels into one validated artifact |
| `reusable-build-pydevices-distributions.yml` | Discover `pydevices/lib` leaves and `utils` desktop payload; build every exact-version distribution |
| `reusable-request-mip-publication.yml` | Dispatch the exact repository, ref, version, and profile to the central queue |
| `reusable-synchronize-mip-package.yml` | Synchronize one source release, validate the complete latest-only index, create one source commit, and stage the Pages artifact |
| `reusable-validate-pyscript-filesystem-toml.yml` | Reject stale generated PyScript filesystem mappings |

The shared scripts use descriptive operation names and filesystem discovery;
new publishable sources are picked up without an include list. PyScript TOMLs
contain runtime filesystem mappings, not package metadata.

Changing a reusable workflow contract is an automation rollout, not a package
release. Validate it independently, create a new stable publishing ref when
the contract changes, update coordinators deliberately, and only then use that
ref for future package versions.
