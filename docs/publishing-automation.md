# Releasing and publishing PyDevices packages

This is the organization-wide runbook for publishing a new package version, and
it **lives here because it is org-wide**: it governs `palettes`, `pdwidgets`,
`pygraphics`, `audioif`, `pydevices`, `lvgl-python`, and `mpftp`, and it
documents the reusable workflows and shared credentials that this repository
owns.

Repository-specific publishing documents cover only what their own release
produces — for example
[pydevices/docs/publishing.md](https://github.com/PyDevices/pydevices/blob/main/docs/publishing.md)
describes that repo's dynamically discovered package set. They add build or
test details; they do not restate or replace the procedure below.

A **published GitHub Release named `vX.Y.Z` is the authoritative release
event**. The source tag selects the exact files to build, and `X.Y.Z` becomes
the package version. A manual workflow run is only a retry of an existing
exact tag; it is not a way to publish an untagged branch or a different
commit.

## The tag contract

Every publishing repository's coordinators pin the reusable workflows in this
repository at a tag, not a branch, so a change here does not alter a release
until the tag moves:

```yaml
uses: PyDevices/.github/.github/workflows/reusable-publish-release-packages.yml@publishing-v6
```

**`publishing-v6` is current.** Tags `publishing-v1` through `publishing-v6`
all still exist, so a release cut before a contract change can still be
retried against the exact contract it was built with. Each tag's nested
`uses:` refs point at its own tag, so a caller on `v3` runs an entirely `v3`
chain.

Publishing tags are **immutable by policy, and that policy is enforced**, not
just documented: this repository has a tag ruleset named "publishing tags are
immutable" (`target: tag`, `enforcement: active`) that blocks moving or
deleting a `publishing-v*` tag. Cut a new tag for a new contract; never force-
push an existing one.

## What each repository publishes

| Source repository | TestPyPI | PyDevices MIP index |
|---|---|---|
| `palettes` | `pydevices-palettes` wheel and sdist | `palettes` |
| `pdwidgets` | `pydevices-pdwidgets` wheel and sdist | `pdwidgets` |
| `pygraphics` | `pydevices-pygraphics` Linux, Windows, Android, and WASM wheels | Pure-Python `pygraphics` |
| `audioif` | `pydevices-audioif` (native/WASM), plus `pydevices-audioinstruments` and `pydevices-audioeffects` (pure-Python) — three distributions from one repository | `audioinstruments` and `audioeffects` — the pure-Python tier only; the native modules are firmware, built from the usermod source |
| `pydevices` | `pydevices` (all of `lib/`) and `pydevices-desktop` | One package per `lib/` component, plus `pydevices` and `pydevices-desktop` |
| `lvgl-python` | `pydevices-lvgl` Linux, Windows, Android, and WASM wheels | Nothing |
| `mpftp` | `pydevices-mpftp` wheel and sdist | Nothing |

The pip distribution names are prefixed with `pydevices-`; MIP package names
are not. `pydevices` and `pydevices-desktop` keep the same name in both
systems. `mpftp` additionally has its own `publish-vsix.yml`, unrelated to
this chain, which publishes the VS Code extension to the VS Marketplace and
Open VSX using `VSCE_PAT` / `OVSX_PAT` (both optional; the steps skip when
unset).

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
  desktop stack.
- All artifacts from one `pydevices` release share a version.
- MIP meta-package dependencies resolve `latest` from the latest-only index.
- Only `pydevices` and `pydevices-desktop` declare `pypi_publish`; the MIP leaf
  packages deliberately do not, because they have no PyPI distribution of their
  own.
- Board `package.json` installers are not copied into the central MIP index.
  Install them from their documented raw GitHub paths; the desktop board
  library files themselves remain part of `pydevices-desktop`.

Adding or removing a publishable entry under `lib/` or `utils/` therefore
changes the next release automatically. Review the generated package set as
part of release preparation. Committed root TOML files (such as
`pydevices-desktop.toml` and `pydevices-examples.toml`) are PyScript
filesystem mappings of the repository payloads, not package metadata; their
CI validation must pass before release.

## Standard release procedure: the release-PR flow

Every one of the seven publishing repositories now uses the same three-
workflow chain instead of hand-writing `VERSION` and tagging locally. It
exists to keep the human choice of version — the org's one deliberate
exception to full automation — while removing the manual tag/push/release
sequence that used to precede it.

```text
Prepare release (workflow_dispatch, optional version)
  -> bot opens a release PR carrying VERSION + CHANGELOG.md
  -> a human confirms or edits the version on that PR
  -> merge to main
  -> Tag release creates the vX.Y.Z tag and GitHub Release (via the App)
  -> Publish release packages: build -> TestPyPI -> assets attached
     -> MIP (final releases only) -> health report
```

### 1. Dispatch "Prepare release"

```bash
gh workflow run prepare-release.yml --repo PyDevices/<repository>
# or with a specific version:
gh workflow run prepare-release.yml --repo PyDevices/<repository> -f version=X.Y.Z
```

This runs `reusable-prepare-release-pr.yml`. The `version` input is optional
and is only ever a **suggestion**: leaving it empty computes the highest
existing `vX.Y.Z` tag plus one patch, but that computed value — and any
explicitly requested value — is not committed until a human confirms it. The
workflow:

1. Resolves the version (requested value, or the computed suggestion),
   rejecting anything that doesn't match
   `X.Y.Z[{a|b|rc}N|.devN]` or a tag that already exists.
2. Writes that version to `VERSION` and prepends a new `## vX.Y.Z (date)`
   section to `CHANGELOG.md`, built from `git log` since the last tag.
3. Opens (or updates) a PR titled `Release X.Y.Z` from branch
   `release/vX.Y.Z`, with an explicit note: **"The version is yours to
   change — edit VERSION on this branch before merging if X.Y.Z is not the
   right call. Merging tags the version in VERSION and triggers publication;
   closing publishes nothing."**

### 2. Review and merge the release PR

This is the human checkpoint. Confirm the suggested version is correct (or
push a commit to the PR branch changing `VERSION` to the right one),
review the generated changelog section, confirm CI is green, then merge.
Closing the PR without merging publishes nothing.

### 3. Tag release fires automatically

`reusable-tag-on-release-merge.yml` runs on every push to `main` that touches
`VERSION`. It:

1. Diffs `VERSION` against the previous commit; does nothing if unchanged or
   if the tag already exists.
2. Mints a GitHub App token (`PYDEVICES_APP_ID` / `PYDEVICES_APP_PRIVATE_KEY`)
   and creates the `vX.Y.Z` tag and GitHub Release at that commit, marking it
   `--prerelease` when the version has a `{a|b|rc}N` or `.devN` suffix.

The App token is required here, not incidental: **a Release created with the
default `GITHUB_TOKEN` does not trigger `on: release` workflows**, so the
publish chain below would silently never fire.

### 4. Publish release packages runs from the Release event

`reusable-publish-release-packages.yml` resolves and validates the `vX.Y.Z`
tag, builds (pure-Python, native-and-wasm, or pydevices-multi, per caller),
publishes to TestPyPI, attaches the built artifacts to the GitHub Release,
optionally publishes to production PyPI, requests MIP publication for final
releases, and reports to the Release Health dashboard regardless of outcome.
See "How the release chain is wired" below for the per-job detail.

### Manual tag + release: the fallback

The release-PR flow is the default, but a manual tag and Release remain a
valid fallback — for a hotfix, a recovery, or any release where opening a PR
is impractical. The one hard rule does not change: **the tag and the
committed `VERSION` file must match exactly**, because the build jobs
(`reusable-build-pure-python-distribution.yml`,
`reusable-build-native-and-wasm-wheels.yml`,
`reusable-build-pydevices-distributions.yml`) reject a mismatch outright.

```bash
cd <workspace-root>/<repository>
git switch main && git pull --ff-only

version=X.Y.Z
printf '%s\n' "$version" > VERSION
git add VERSION CHANGELOG.md
git commit -m "Release ${version}"
git push origin main

release_commit="$(git rev-parse HEAD)"
gh release create "v${version}" \
  --repo PyDevices/<repository> \
  --target "$release_commit" \
  --title "v${version}" \
  --generate-notes
```

`gh release create` with a user token triggers `on: release` normally (only
the App-token requirement above is specific to the automated tag step, which
runs with a plain `GITHUB_TOKEN` context). `gh release create` publishes
immediately unless `--draft` is supplied; if a release is prepared in the
GitHub web UI, select the exact version commit, create `vX.Y.Z`, and
**Publish release** — merely pushing a tag or saving a draft does not trigger
the coordinator.

## Automation and credentials

Each publishing repository has three thin coordinators
(`prepare-release.yml`, `tag-release.yml`, `publish-release-packages.yml`),
each calling one reusable workflow from this repository and supplying only
what differs:

```yaml
jobs:
  publish:
    uses: PyDevices/.github/.github/workflows/reusable-publish-release-packages.yml@publishing-v6
    with:
      build-kind: pure-python          # or native-and-wasm, pydevices-multi
      distribution-name: pydevices-palettes
      import-name: palettes
      mip-profile: palettes            # comma-separate for several, as audioif does; omit to skip MIP
      release-ref: ${{ inputs.release-ref }}
    secrets: inherit
```

`audioif` is the outlier: its `publish-release-packages.yml` runs a shared
`parity` gate (the four `tests/parity/verify_*.py` scripts) and a
`credentials` check job, then three separate calls into the reusable chain —
one `native-and-wasm` build for `pydevices-audioif` with
`mip-profile: audioinstruments,audioeffects`, and two `pure-python` builds
(`pydevices-audioinstruments`, `pydevices-audioeffects`) from
`lib/audioinstruments` and `lib/audioeffects`, each with no `mip-profile` of
its own (their MIP publication rides on the first job's comma-separated
profile list, since all three come from the same tag).

Required secrets:

| Secret | Where needed | Purpose |
|---|---|---|
| `PYDEVICES_APP_ID`, `PYDEVICES_APP_PRIVATE_KEY` | Every publishing repository, `PyDevices/mip` | Mint short-lived GitHub App installation tokens: to open release PRs, to create tags/Releases (so `on: release` fires), to dispatch the MIP queue, and to dispatch the Release Health report |
| `TESTPYPI_API_TOKEN` | Every repository that uploads to TestPyPI | API token for the `bdbarnett` TestPyPI account |
| `VSCE_PAT`, `OVSX_PAT` | **`mpftp` only** (`publish-vsix.yml`, unrelated to this chain) | VS Marketplace and Open VSX. Both optional; the steps skip when unset |

TestPyPI still uses token authentication (`user: __token__`, `password:
${{ secrets.TESTPYPI_API_TOKEN }}`, `repository-url:
https://test.pypi.org/legacy/`, `skip-existing: true`) — it is not Trusted
Publishing, and that is deliberate: TestPyPI Trusted Publishing has its own
per-repo/workflow/environment registration that has not been set up.

### Production PyPI: opt-in, protected, Trusted Publishing

Publishing to **production** PyPI (as opposed to TestPyPI, which every
release always reaches) is a separate, explicit, per-package decision via the
`pypi-publish: true` input on `reusable-publish-release-packages.yml`. As of
this writing no caller sets it — every current release stops at TestPyPI plus
MIP. When a package does opt in, `publish-to-pypi`:

- runs only for a **final** release (`prerelease == 'false'`; a `.devN` or
  `{a|b|rc}N` build never reaches PyPI),
- runs through the repository's `pypi` **GitHub Environment**, which exists
  in all seven publishing repositories and is configured with required
  reviewers and a branch policy (confirmed via
  `gh api repos/PyDevices/<repo>/environments/pypi`), and
- authenticates via **PyPI Trusted Publishing** (OIDC, `id-token: write`,
  `pypa/gh-action-pypi-publish@release/v1` with no token) — no long-lived
  PyPI credential is stored anywhere.

Enabling `pypi-publish` for a package therefore requires both flipping the
input in that repository's coordinator *and* a matching Trusted Publisher
already configured on the PyPI project for that repository/workflow/
environment. Do one before the other and the run fails safely at the PyPI
end, not silently.

## The LVGL model

`lvgl-python`, `lvgl-micropython`, and `lvgl-circuitpython` all consume
generated bindings from `lvgl-bindings`, which is the **single writer** of
the generated C, the `.pyi` stub, and the sync-relevant support files
(`lv_conf.h`, `display_driver.py`, `fs_driver.py`, the `lvgl` submodule
pointer). Hand-editing any of that in a consumer repo is overwritten by the
next sync — see CONTRIBUTING.md.

The trigger is explicit dispatch, not a webhook chain:

```text
lvgl-bindings: Release bindings (workflow_dispatch, bindings-ref, publish=true)
  -> validates the exact ref, runs the linux-integration matrix,
     runs the non-mutating release_dry_run.sh gate
  -> if publish=true: mints a GitHub App token scoped to lvgl-python
     and dispatches lvgl-python's sync-and-release.yml
       -f lvgl_bindings_ref=<exact commit sha> -f mode=release

lvgl-python: Sync and release (workflow_dispatch, lvgl_bindings_ref, mode)
  -> ./scripts/sync_from_lvgl_bindings.sh --ref <ref>
  -> writes/commits LVGL_BINDINGS_COMMIT, VERSION, generated/lvgl_python.c,
     generated/lvgl.pyi, lv_conf.h, display_driver.py, fs_driver.py, lvgl
  -> builds + runs its test suite + the lvgl-bindings smoke suite
  -> mode=release: mints an App token, publishes vX.Y.Z (App token, same
     reasoning as tag-release.yml -- GITHUB_TOKEN would not trigger
     publish-release-packages.yml)
```

`mode` also accepts `dry-run` (validate only, nothing committed) and `sync`
(commit the sync, no release) for exercising the pipeline without publishing.
`lvgl-micropython` and `lvgl-circuitpython` each carry their own
`scripts/sync_from_lvgl_bindings.sh` and an `LVGL_BINDINGS_COMMIT` file
recording what they last synced, but neither has a `.github/workflows/`
directory of its own — their sync is run by hand (or from the maintainer
orchestration in `cmods`), not on a schedule or dispatch chain.

`lvgl-bindings/check-dispatch-token.yml` is a read-only diagnostic (does the
App token reach `lvgl-python`?) kept until the App path has enough track
record to retire it; it does not trigger anything.

The previously documented `trigger-lvgl-python-release.yml` and
`LVCPYTHON_MOD_DISPATCH_TOKEN` (a PAT-based dispatch mechanism) are
**retired** — `lvgl-bindings` has no such workflow and no such secret
reference today. The App-token dispatch above replaced it.

Once `lvgl-python`'s Release publishes, `publish-release-packages.yml` there
runs the ordinary `native-and-wasm` build for `pydevices-lvgl` with no
`mip-profile` — `lvgl-python` does not publish to the MIP index.

## The MIP publication queue

Publishing to the MIP index is centralized in `PyDevices/mip` and
**serialized**: `process-mip-publication-request.yml` runs in the
`pydevices-mip-publication-queue` concurrency group with
`cancel-in-progress: false`, so two releases that both want MIP entries never
race — the second waits for the first to finish.

### Request → queue → sync

`reusable-request-mip-publication.yml` (called from a publishing repository
with `secrets: inherit`) mints an App token scoped to `mip` and dispatches
one `repository_dispatch` per profile in the (possibly comma-separated)
`mip-profile` input — `audioif` sends two in the same release. This only
happens for **final releases**: `request-mip-publication`'s `if:` requires
`prerelease == 'false'`, so a `.devN`/`rcN` build never reaches the MIP
index, only TestPyPI.

The queue consumer, `reusable-synchronize-mip-package.yml`:

1. Checks out `mip` at the **`PyDevices` branch tip**, not the SHA frozen at
   dispatch time. This is deliberate: a `repository_dispatch` payload freezes
   `github.sha` at creation time, so the second of two queued publications
   (audioif's two profiles) would otherwise check out a tree that predates
   the first one's lockfile commit and lose its push as a non-fast-forward —
   this happened in practice and left `audioinstruments` a release behind
   `audioeffects` in the live index for two days.
2. Records the release in `pydevices-lock.json` — the source of truth for
   "what version of each package is currently live." Every publishable
   package must already have an entry in the lockfile; a new profile is
   added there deliberately, not auto-created.
3. **Re-synchronizes every locked source**, not just the one being released:
   it clones each `{repository, ref}` pair from the (now-updated) lockfile
   and runs `synchronize_mip_package.py` for each, because `build.py`
   compiles every `manifest.py` in the tree at once — there is no way to
   rebuild one package's index entry in isolation.
4. Removes the temporary `.publication-sources` checkouts, builds the
   complete latest-only index, and verifies every expected manifest produced
   an index entry and that each locked package's index version matches the
   lockfile.
5. Commits the lockfile with **rebase-and-retry**, not fail-fast: up to 3
   attempts of `git push` → on rejection, `git pull --rebase` → retry. The
   concurrency group already serializes same-repo runs, but this covers a
   push that lands from elsewhere between checkout and push.
6. Assembles and uploads the GitHub Pages artifact; a separate
   `deploy-complete-mip-index` job in the caller workflow deploys it via
   `actions/deploy-pages@v4`.

### Manual dispatch

`process-mip-publication-request.yml` also accepts `workflow_dispatch` for
recovery, with `profile` as a fixed choice input covering every current
profile:

```bash
gh workflow run process-mip-publication-request.yml \
  --repo PyDevices/mip \
  -f source-repository=PyDevices/<repository> \
  -f source-ref=vX.Y.Z \
  -f version=X.Y.Z \
  -f profile=<palettes|pdwidgets|pygraphics|pydevices|audioinstruments|audioeffects>
```

Use a direct central dispatch only for recovery after confirming the source
tag and profile are correct. The normal entry point is always a publishing
repository's own release, not this fallback.

## Retrying an interrupted publication

Never move the tag or rebuild the same version from a different commit.
Retry the coordinator with the exact existing tag:

```bash
gh workflow run publish-release-packages.yml \
  --repo PyDevices/<repository> \
  -f release-ref=vX.Y.Z
```

The workflows check out that tag, revalidate it, and use
`skip-existing: true` for TestPyPI. This safely completes a partial upload
without replacing files that TestPyPI already accepted.

If only the current MIP run or Pages deployment failed, retry its failed
jobs:

```bash
gh run rerun <mip-run-id> --repo PyDevices/mip --failed
```

If the shared reusable-workflow ref changed after the failed run, GitHub's
**rerun** operation may remain pinned to the reusable workflow commit
selected by the original attempt. Start a fresh source exact-tag retry, or
use the manual MIP dispatch above.

## Correcting a bad release

Published TestPyPI files and released source tags are immutable in practice.
Deleting a GitHub Release does not remove registry files, and moving a tag
would make the release irreproducible (and the tag ruleset would refuse the
move on this repository's own `publishing-v*` tags in any case).

To correct a release:

1. Fix the source on `main`.
2. Run "Prepare release" again for a new version.
3. Repeat the release-PR flow (or the manual fallback).
4. Yank an unusable TestPyPI version only when necessary and document why; do
   not attempt to upload replacement files under the same version.

Publishing the corrected MIP version replaces the affected package's `latest`
entry when the central latest-only index is deployed.

## The Release Health dashboard

Every `publish-release-packages` run — success or failure — ends with a
`report-release-health` job (`continue-on-error: true`, so a reporting
failure never fails the release itself) that dispatches a
`repository_dispatch` of type `release-health` to `PyDevices/.github`, with
the run's outcome for each stage (TestPyPI, assets, MIP, PyPI). This
repository's `release-health.yml` folds that payload into
[`release-health/data.json`](../release-health/data.json) and regenerates
[`RELEASE_HEALTH.md`](../RELEASE_HEALTH.md) at the repo root — one row per
distribution, linking back to the run that produced it.

## Troubleshooting

| Symptom | Meaning and response |
|---|---|
| No publication run after pushing a tag | A tag alone is not the trigger. Publish the GitHub Release. |
| `VERSION contains ... but the release tag is ...` | Fix and commit `VERSION`, then create a **new** tag/version via a fresh "Prepare release" run. Do not move a published tag. |
| TestPyPI `invalid-publisher` | The job attempted OIDC Trusted Publishing without a matching publisher. TestPyPI still uses `__token__` + `TESTPYPI_API_TOKEN`. |
| TestPyPI authentication failure | Confirm that `TESTPYPI_API_TOKEN` exists in that source repository, belongs to `bdbarnett`, has permission for the project, and has not expired or been revoked. |
| TestPyPI duplicate-file response | Retry with the current coordinator, which sets `skip-existing: true`; otherwise publish a new version. |
| Production PyPI publish did not run | Check three things: `pypi-publish: true` on the caller, the release is a final version (not `.devN`/`{a,b,rc}N`), and the `pypi` environment's required reviewers approved the run. |
| MIP request is queued | Expected — the central concurrency group processes publication requests serially. |
| MIP validation sees `.publication-sources/manifest.py` | The shared synchronization job did not remove temporary checkouts; start a fresh run on a current `publishing-v*` tag. |
| Pages setup or action download returns 429/503/504 | Usually transient GitHub infrastructure trouble. Retry the failed MIP job and verify the live index afterward. |
| Source workflow succeeds but MIP is still old | Inspect the downstream `PyDevices/mip` run and wait for the Pages deployment; source success only confirms dispatch. |
| A native wheel platform is missing | Fix the wheel matrix and publish a new version. TestPyPI cannot accept a replacement with an existing filename. |
| `RELEASE_HEALTH.md` shows a stale row | The reporting job runs `continue-on-error`; a real failure elsewhere in the chain does not block it, but a `PyDevices/.github` outage or a missing App installation would. Check the linked run URL directly. |

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

`reusable-publish-release-packages.yml` is the whole per-repository release
chain: it resolves the tag, dispatches the matching build (`build-pure-python`
/ `build-native-and-wasm` / `build-pydevices-multi`, exactly one of which runs
per invocation, selected by `build-kind`), publishes to TestPyPI, attaches
release assets, requests MIP publication, optionally publishes to production
PyPI, and reports to Release Health — all as jobs inside that one reusable
workflow, not separate coordinators. It replaced five near-identical copies of
the same three jobs.

Changing a reusable workflow contract is an automation rollout, not a package
release. Validate it independently, create a new stable publishing tag when
the contract changes, update coordinators deliberately, and only then use
that tag for future package versions.

## Shared implementation reference

For the workflows *outside* this release chain — the Pages `deploy.yml`
pipeline, test and lint jobs, and validators — see [workflows.md](workflows.md).

| Workflow | Responsibility |
|---|---|
| `reusable-prepare-release-pr.yml` | Open the release PR: compute the version suggestion, write `VERSION` + `CHANGELOG.md`, push, open/update the PR |
| `reusable-tag-on-release-merge.yml` | On a merged `VERSION` change, create the `vX.Y.Z` tag and GitHub Release with the App token |
| `reusable-publish-release-packages.yml` | The whole release chain: resolve the tag, build, publish to TestPyPI, attach assets, request MIP publication, optionally publish to PyPI, report health |
| `reusable-build-pure-python-distribution.yml` | Build, check, clean-install, and upload one wheel/sdist artifact |
| `reusable-build-native-and-wasm-wheels.yml` | Build Linux, Windows, Android, and WASM (Pyodide) wheels into one validated artifact |
| `reusable-build-pydevices-distributions.yml` | Discover `pydevices/lib` leaves and `utils` desktop payload; build every exact-version distribution |
| `reusable-request-mip-publication.yml` | Dispatch the exact repository, ref, version, and profile(s) to the central MIP queue |
| `reusable-synchronize-mip-package.yml` | Re-synchronize every locked source, validate the complete latest-only index, create one lockfile commit, and stage the Pages artifact |
| `reusable-validate-pyscript-filesystem-toml.yml` | Reject stale generated PyScript filesystem mappings |
| `release-health.yml` | Fold a `release-health` dispatch into `release-health/data.json` and regenerate `RELEASE_HEALTH.md` |

The shared scripts use descriptive operation names and filesystem discovery;
new publishable sources are picked up without an include list. PyScript TOMLs
contain runtime filesystem mappings, not package metadata.
