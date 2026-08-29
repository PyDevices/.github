# GitHub Actions workflows

What exists, in which repository, and why. Procedures live elsewhere:
[publishing-automation.md](publishing-automation.md) for releases,
[building-docs.md](building-docs.md) for documentation.

The inventory includes the native `audioif` CPython release caller.

## Reusable workflows (`PyDevices/.github`)

Callers pin a tag, not a branch, so a change here does not alter a release
until the tag moves. **`publishing-v6` is current**; earlier tags
(`publishing-v1`–`publishing-v5`) remain so a release cut before a contract
change can still be retried against the exact contract it was built with.
`publishing-v*` tags are immutable by policy and by an active tag ruleset on
this repository ("publishing tags are immutable") that blocks moving or
deleting them.

| Workflow | Purpose |
|---|---|
| `reusable-prepare-release-pr.yml` | Open the release PR: compute a version suggestion, write `VERSION` + `CHANGELOG.md`, open/update the PR |
| `reusable-tag-on-release-merge.yml` | On a merged `VERSION` change, create the `vX.Y.Z` tag and GitHub Release with the App token |
| `reusable-publish-release-packages.yml` | The whole release chain: resolve the tag, build, publish to TestPyPI, attach assets, request MIP publication, optionally publish to PyPI, report health |
| `reusable-build-pure-python-distribution.yml` | sdist + wheel for a pure-Python package |
| `reusable-build-native-and-wasm-wheels.yml` | cibuildwheel: Linux, Windows, Android, Pyodide wasm32 |
| `reusable-build-pydevices-distributions.yml` | The `pydevices` and `pydevices-desktop` distributions, derived from `lib/` and `utils/` |
| `reusable-request-mip-publication.yml` | Dispatch into `mip`'s serialized publication queue (one dispatch per profile) |
| `reusable-synchronize-mip-package.yml` | Record the release in `pydevices-lock.json`, re-sync every locked source, rebuild and validate the index, stage the Pages artifact |
| `reusable-validate-pyscript-filesystem-toml.yml` | Check a `*.toml` filesystem map against the tree it claims to mirror |
| `release-health.yml` (not reusable; own trigger) | Fold a `release-health` `repository_dispatch` into `release-health/data.json` and regenerate `RELEASE_HEALTH.md` |

The build workflows that need shared scripts also check this repository out,
pinned by `publishing-tools-ref` — which defaults to `publishing-v6`, so
workflows and scripts always come from the same tag.

## Releasing

Each of seven repositories has a `prepare-release.yml` + `tag-release.yml` +
`publish-release-packages.yml` trio. The first two are near-identical
one-job callers; `publish-release-packages.yml` supplies only what differs —
the build kind, the distribution name, and the MIP profile:

| Repository | `build-kind` | Distribution | MIP profile |
|---|---|---|---|
| `pydevices` | `pydevices-multi` | `pydevices` | `pydevices` |
| `palettes` | `pure-python` | `pydevices-palettes` | `palettes` |
| `pdwidgets` | `pure-python` | `pydevices-pdwidgets` | `pdwidgets` |
| `pygraphics` | `native-and-wasm` | `pydevices-pygraphics` | `pygraphics` |
| `audioif` | `native-and-wasm` + 2× `pure-python` | `pydevices-audioif`, `pydevices-audioinstruments`, `pydevices-audioeffects` | `audioinstruments,audioeffects` (on the native job only) |
| `lvgl-python` | `native-and-wasm` | `pydevices-lvgl` | — none |
| `mpftp` | `pure-python` | `pydevices-mpftp` | — none |

`publish-release-packages.yml` triggers on a published GitHub Release, or on
`workflow_dispatch` with an exact `vX.Y.Z` tag to retry one.
`prepare-release.yml` triggers only on `workflow_dispatch` (optional
`version` input). `tag-release.yml` triggers on `push` to `main` touching
`VERSION`.

`audioif` additionally runs a `parity` job (the four
`tests/parity/verify_*.py` acceptance/effects/streaming/biquad gates) and a
`credentials` job (confirms `TESTPYPI_API_TOKEN` is visible) before any of
its three publish jobs.

Cross-repository release plumbing:

| Repository | Workflow | Role |
|---|---|---|
| `lvgl-bindings` | `release.yml` | On explicit `workflow_dispatch` with `publish=true`, mint an App token scoped to `lvgl-python` and dispatch its `sync-and-release.yml` with the exact bindings commit |
| `lvgl-bindings` | `check-dispatch-token.yml` | Manual, read-only diagnostic that the App token can reach `lvgl-python` |
| `lvgl-python` | `sync-and-release.yml` | Sync generated bindings (`LVGL_BINDINGS_COMMIT`, `generated/*`, `lv_conf.h`, drivers), commit, and (`mode=release`) publish a Release with the App token |
| `mpftp` | `publish-vsix.yml` | Build the VSIX and publish to VS Marketplace / Open VSX (`VSCE_PAT` / `OVSX_PAT`, both optional) |
| `android-runner` | `release_apk.yml` | Build the APK that `pydevices/bin/android.py --install-apk` downloads |

> `sync-and-release.yml` mints its own App token to create `lvgl-python`'s
> Release, which looks redundant and is not: **a Release created with
> `GITHUB_TOKEN` does not trigger `on: release` workflows**, so
> `publish-release-packages.yml` there would never fire and nothing would
> reach TestPyPI. The same reasoning is why `reusable-tag-on-release-merge.yml`
> mints an App token for every other repository's tag/Release step too.

`lvgl-micropython` and `lvgl-circuitpython` each carry a
`scripts/sync_from_lvgl_bindings.sh` and their own `LVGL_BINDINGS_COMMIT`,
but neither has a `.github/workflows/` directory — their sync from
`lvgl-bindings` is run by hand, not dispatched by a workflow.

## MIP index (`mip`)

| Workflow | Role |
|---|---|
| `process-mip-publication-request.yml` | Serialized queue consumer (`pydevices-mip-publication-queue` concurrency group, `cancel-in-progress: false`): synchronize a package, rebuild the index, deploy. Accepts `repository_dispatch` (from `reusable-request-mip-publication.yml`) or `workflow_dispatch` with `profile` as a fixed choice of every current profile |
| `deploy-mip-index-to-pages.yml` | Compile and publish the index. Triggers on the **`PyDevices`** branch, not `main` |
| `validate-mip-package-index.yml` | Check index integrity |
| `tests.yml`, `ruff.yml`, `commit-formatting.yml` | Inherited from micropython-lib upstream — leave them alone |

## Testing and validation

| Repository | Workflow | Notes |
|---|---|---|
| `pydevices` | `tests.yml` | Also validates board MIP installers |
| `palettes`, `pdwidgets` | `tests.yml` | Sparse-checkout of sibling repos onto `PYTHONPATH` (`pdwidgets` needs four) |
| `pygraphics` | `tests.yml` | Runs the suite twice — pure Python, then the native extension via `PYGRAPHICS_TEST_NATIVE=1` |
| `audioif` | `tests.yml` | Also the source of the `parity` gate `publish-release-packages.yml` reruns at release time |
| `pydevices-examples` | `tests.yml`, `manifests.yml` | Gallery and install-manifest freshness |
| `pydevices`, `pygraphics` | `validate-pyscript-filesystem-toml.yml` | Standalone callers of the reusable validator. `pdwidgets` and `palettes` call the same reusable as a job inside `tests.yml` |
| `.github` (this repo) | `checks.yml` | actionlint over `.github/workflows`, a YAML-parse smoke test of every reusable, a site-generator idempotency check against checked-out siblings, and `ruff` over `scripts/` |

## Pages

**Two repositories publish Pages**, plus the portal:

| Repository | What it serves |
|---|---|
| `PyDevices.github.io` | The portal **and every repository's landing page**, at `/<repo>/`. Serves from `main`, no workflow |
| `pydevices-examples` | `deploy.yml` — the PyScript gallery: manifest audits and symlink replacement |
| `mip` | `deploy-mip-index-to-pages.yml` — the package index |

Every other landing page is generated by
[`scripts/generate_sites.py`](../scripts/generate_sites.py) into the portal
repository from [`data/repos_db.json`](../data/repos_db.json). Where a page goes
is the entry's `page` field: `portal-root`, `portal-subdir`, `self`,
`self-subpath`, or `none`. There are no per-repo `deploy.yml` files and no
`gh-pages` branches; thirteen of each were removed once the portal took over
those paths.

> A landing page is a single `index.html` referencing `/assets/chrome/`
> and `/assets/img/logo.svg` at the portal root.

## Documentation

**No repository builds documentation in Actions.** ReadTheDocs builds
`palettes`, `pdwidgets`, and `pygraphics` on push via the org GitHub App. A
duplicate `mkdocs build` used to run here too and was deleted: it passed while
two of the three sites were failing to publish, because `mkdocs` exits 0 and RTD
then fails the build on output checks `mkdocs` cannot see.

## Maintenance

`dependabot.yml` watches pinned action versions in the repositories that have
workflows, grouped into one weekly PR each. `mip` is excluded — its
workflows come from upstream.

## Conventions

- Pin actions to a major version (`actions/checkout@v7`).
- Logic shared by more than one repository belongs in a `reusable-*.yml` here,
  called at a pinned `publishing-v*` tag.
- Path filters on `push` and `pull_request`; `workflow_dispatch` on anything you
  might need to re-run by hand.
- A workflow that writes to another repository needs a token in `secrets`;
  `GITHUB_TOKEN` cannot reach across repositories, and cannot trigger another
  workflow even within one — hence the App-token pattern used for tagging,
  MIP dispatch, and the LVGL sync dispatch.
