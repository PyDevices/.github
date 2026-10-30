# GitHub Actions workflows

What exists, in which repository, and why. The procedures are in
[release a package](../guides/release-a-package.md) and
[build and publish documentation](../guides/build-and-publish-docs.md); the
design of the release chain is in [the release chain](../how-it-works/release-chain.md).
Inputs, secrets and tags are in [release workflows](release-workflows.md).

## Reusable workflows in this repository

| Workflow | Purpose |
|---|---|
| `reusable-prepare-release-pr.yml` | Open the release PR: compute a version suggestion, write `VERSION` and `CHANGELOG.md`, open or update the PR |
| `reusable-tag-on-release-merge.yml` | On a merged `VERSION` change, create the `vX.Y.Z` tag and GitHub Release with the App token |
| `reusable-publish-release-packages.yml` | The whole release chain: resolve the tag, build, publish to TestPyPI, attach assets, request MIP publication, tell the caller whether to publish to PyPI, report health |
| `reusable-report-pypi-result.yml` | Report a caller-side PyPI upload to Release Health ([why the upload is caller-side](../guides/publish-to-pypi.md)) |
| `reusable-build-pure-python-distribution.yml` | sdist and wheel for a pure-Python package |
| `reusable-build-native-and-wasm-wheels.yml` | cibuildwheel: Linux, Windows, Android and Pyodide wasm32 |
| `reusable-build-pydevices-distributions.yml` | The `pydevices` and `pydevices-desktop` distributions, derived from `lib/` and `utils/` |
| `reusable-request-mip-publication.yml` | Dispatch into the publication queues of `mip` and `lib`, once per profile |
| `reusable-synchronize-mip-package.yml` | Record the release in `pydevices-lock.json`, re-sync every locked source, rebuild and validate the index, stage the Pages artifact |
| `reusable-validate-pyscript-filesystem-toml.yml` | Check a `*.toml` filesystem map against the tree it claims to mirror |

Callers name a reusable by tag (`@publishing-vN`), never by branch. The build
workflows that need this repository's scripts check it out at
`publishing-tools-ref`, which defaults to the tag the workflow itself is at.

## Workflows that run here

| Workflow | Trigger | What it does |
|---|---|---|
| `checks.yml` | push to `main`, pull request | actionlint over the workflows; a YAML parse of each; the site generator's idempotency check against fresh clones of the repositories it writes to; a check that the reusables' references agree on one tag; `ruff` over `scripts/` and `tests/`; the script tests; the main documentation build |
| `release-health.yml` | `repository_dispatch` from a publish run | Fold the report into `release-health/data.json` and regenerate `RELEASE_HEALTH.md` |
| `hero-check.yml` | daily, and by hand | Load each published demo in a browser; open or update an issue when one is dead |
| `cold-eyes-review.yml` | quarterly, and by hand | Open the [review issue](../guides/maintenance-schedule.md#quarterly) |

## Releasing

Six repositories release through the reusable chain. Five of them
(`pydevices`, `pygraphics`, `audiodsp`, `audiocomponents` and `mpftp`) carry a
`prepare-release.yml`, `tag-release.yml` and `publish-release-packages.yml`
trio. The first two are one-job callers; `publish-release-packages.yml` supplies
what differs, the build kind, the distribution name and the MIP profile:

| Repository | `build-kind` | Distribution | MIP profile |
|---|---|---|---|
| `pydevices` | `pydevices-multi` | `pydevices` (and `pydevices-desktop`) | `pydevices` |
| `pygraphics` | `native-and-wasm` | `pydevices-pygraphics` | `pygraphics` |
| `audiodsp` | `native-and-wasm` | `omnipython-audiodsp` | none |
| `audiocomponents` | `pure-python`, twice | `pydevices-audioinstruments`, `pydevices-audioeffects` | `audioinstruments,audioeffects` |
| `mpftp` | `pure-python` | `pydevices-mpftp` | none |
| `omnipython-lvgl` | `native-and-wasm` | `pydevices-lvgl` | none |

`publish-release-packages.yml` triggers on a published GitHub Release, or on
`workflow_dispatch` with an exact `vX.Y.Z` tag to retry. `prepare-release.yml`
triggers only on `workflow_dispatch`, with an optional `version` input.
`tag-release.yml` triggers on a push to `main` that touches `VERSION`.
`omnipython-lvgl` has no prepare or tag workflow: its `release.yml` does both
(below).

`audiodsp` runs a `parity` job (the `tests/parity/verify_*.py` gates and every
DSP probe) and a `credentials` job (confirms `TESTPYPI_API_TOKEN` is visible)
before its publish job. `audiocomponents` runs the same kind of gates and
credentials check before its two.

Releases that don't use the trio:

| Repository | Workflow | Role |
|---|---|---|
| `omnipython-lvgl` | `release.yml` | By hand: with `mode=dry-run`, run every gate and change nothing; with `mode=release`, also write the next version to `VERSION` on `main` and publish a GitHub Release, which starts `publish-release-packages.yml` |
| `pydevices` | `tag-package-release.yml`, `publish-package-release.yml` | Release the `palettes` and `pdwidgets` folders on their own `palettes-vX.Y.Z` and `pdwidgets-vX.Y.Z` tags: build the distribution from the folder at the tag and upload it to TestPyPI, then ask the library index for it |
| `pydevices` | `publish-lib-boards.yml` | Ask the library index for board configurations and drivers when they merge |
| `mpftp` | `publish-vsix.yml` | Build the VS Code extension and publish it to VS Marketplace and Open VSX (`VSCE_PAT`, `OVSX_PAT`, both optional) |
| `android-runner` | `release_apk.yml` | Build the APK that `pydevices/bin/android.py --install-apk` downloads |

> A Release created with `GITHUB_TOKEN` doesn't trigger `on: release`
> workflows. That is why `reusable-tag-on-release-merge.yml` and
> `omnipython-lvgl`'s `release.yml` create the Release with an App token.

## The MIP and library indexes

| Repository | Workflow | Role |
|---|---|---|
| `mip` | `process-mip-publication-request.yml` | Queue consumer (`pydevices-mip-publication-queue` concurrency group, `cancel-in-progress: false`): synchronize a package, rebuild the index, deploy. Accepts `repository_dispatch` (from `reusable-request-mip-publication.yml`) or `workflow_dispatch` with `profile` as a fixed choice |
| `mip` | `deploy-mip-index-to-pages.yml` | Rebuild every locked package and publish the index. Triggers on the **`PyDevices`** branch, not `main` |
| `mip` | `validate-mip-package-index.yml`, `refresh-package-list.yml` | Check index integrity; refresh the committed package list from each deployed index |
| `mip` | `tests.yml`, `ruff.yml`, `commit-formatting.yml` | Inherited from micropython-lib; leave them alone |
| `lib` | `publish.yml`, `test.yml` | Build the library index from `pins.json` and deploy it; the builder's tests |

## Testing and validation

| Repository | Workflows |
|---|---|
| `pydevices` | `tests.yml`; `palettes.yml` and `pdwidgets.yml` for those folders; `appkit.yml`; `validate-pyscript-filesystem-toml.yml` |
| `pygraphics` | `tests.yml` (pure Python, then the native extension with `PYGRAPHICS_TEST_NATIVE=1`); `validate-pyscript-filesystem-toml.yml` |
| `audiodsp` | `test-cpython.yml`, `clean-build.yml`, `lint.yml`, `android-wheels.yml`; the parity gates also rerun at release time |
| `audiocomponents` | `tests.yml`, `lint.yml` |
| `omnipython-lvgl` | `generator-checks.yml`, `linux-integration.yml`, `font-drift.yml` |
| `gallery` | `manifests.yml` (install-manifest freshness) |
| `.github` (this repository) | `checks.yml` |

## Pages

| Repository | What it serves |
|---|---|
| `PyDevices.github.io` | The portal and every repository's landing page at `/<repo>/`. Serves from `main` with no workflow |
| `gallery` | `deploy.yml`: the PyScript gallery |
| `mip` | `deploy-mip-index-to-pages.yml`: the package index |
| `lib` | `publish.yml`: the library index |

Every other landing page is generated by
[`scripts/generate_sites.py`](../../scripts/generate_sites.py) into the portal
repository from [`data/repos_db.json`](../../data/repos_db.json). The entry's
`page` field says where a page goes: `portal-root`, `portal-subdir`, `self`,
`self-subpath` or `none`. A landing page is one `index.html` that references
`/assets/chrome/` and `/assets/img/logo.svg` at the portal root.

## Documentation

Read the Docs builds the main project, `palettes`, `pdwidgets` and `pygraphics`
on push through the organization's GitHub App, with `fail_on_warning: true`.
Repositories with a `docs.yml` build the same way in CI (`sphinx-build -W`),
so a warning fails the pull request before it can fail the published build.

## Dependabot

Each repository with workflows has a `dependabot.yml` that watches pinned
action versions, in one grouped weekly pull request.

## Conventions

- Pin actions to a major version (`actions/checkout@v7`).
- Logic shared by more than one repository belongs in a `reusable-*.yml`
  here, called at a pinned `publishing-v*` tag.
- Path filters on `push` and `pull_request`; `workflow_dispatch` on anything
  you might need to run by hand.
- A workflow that writes to another repository needs a token from `secrets`.
  `GITHUB_TOKEN` can't reach across repositories and can't start another
  workflow even within one, hence the App-token pattern for tagging, MIP
  dispatch and the LVGL release.
