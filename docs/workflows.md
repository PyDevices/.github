# GitHub Actions workflows across the organization

An inventory of every workflow in the PyDevices repositories: which are shared,
which are per-repo, and which deliberately differ. **Depth lives elsewhere** —
this page says what exists and who owns it, and points at the runbook or guide
that explains each area.

| Area | Reference |
|---|---|
| Releasing and publishing packages | [publishing-automation.md](publishing-automation.md) |
| The three library documentation sites | [building-docs.md](building-docs.md) |
| Which repos publish a Pages site at all | [data/repos_db.json](../data/repos_db.json) |

As of 2026-08-18 there are 47 workflow files across 18 repositories.

---

## Reusable workflows (this repository)

Called by other repositories at a stable ref, `PyDevices/.github@publishing-v1`.
Changing one is an automation rollout, not a package release — see the runbook.

| Workflow | Responsibility |
|---|---|
| `reusable-build-pure-python-distribution.yml` | Build, check, clean-install, and upload one wheel/sdist artifact |
| `reusable-build-native-and-wasm-wheels.yml` | Build Linux, Windows, Android, and PyEmscripten wheels into one validated artifact |
| `reusable-build-pydevices-distributions.yml` | Discover `pydevices/lib` leaves and the `utils` desktop payload; build every exact-version distribution |
| `reusable-request-mip-publication.yml` | Dispatch repository, ref, version, and profile to the central MIP queue |
| `reusable-synchronize-mip-package.yml` | Synchronize one source release, validate the latest-only index, commit, and stage the Pages artifact |
| `reusable-validate-pyscript-filesystem-toml.yml` | Reject stale generated PyScript filesystem mappings |

---

## `deploy.yml` — the Pages pipeline

**The most replicated workflow in the organization: 12 byte-identical copies,
plus two deliberate variants.** It is what makes the *Pages = marketing* rule
work, and it is easy to delete by accident because nothing else references it.

Every repository listed in [repos_db.json](../data/repos_db.json) must have one,
paired with a checked-in `.site/` directory. Landing pages are generated into
`.site/` from that database by
[scripts/generate_sites.py](../scripts/generate_sites.py); `deploy.yml` is what
publishes them.

The standard form triggers on pushes touching `.site/**` or itself, copies
`.site/*` into `_site/`, touches `.nojekyll`, and pushes to the `gh-pages`
branch with `peaceiris/actions-gh-pages@v4`.

Two repositories differ, on purpose:

| Repository | How it differs |
|---|---|
| `pydevices` | Also copies `bin/micropython.mjs` and `bin/micropython.wasm` into `_site/bin/`. Browser clients fetch that WebAssembly pair from Pages, so dropping it breaks them. `.site/` here is a landing page **plus redirect stubs** for the retired `pydevices.github.io/pydevices/<page>.html` URLs from before the docs became markdown. |
| `pydevices-examples` | Publishes the PyScript gallery, so it does real work first: audits install-manifest freshness, checks gallery manifests, replaces symlinks under `_site/pyscript` with real trees, and stamps the PWA `CACHE_NAME` from a hash of the shell. |

Two repositories in `repos_db.json` have **no** `deploy.yml`, correctly:

- **`mip`** uses its own `deploy-mip-index-to-pages.yml` (below).
- **`PyDevices.github.io`** serves the repository root directly; there is nothing
  to assemble.

Two repositories have no Pages site at all, by design — `.github` (this
repository) and `pydevices-android-runner`. Both are recorded with reasons in
`repos_db.json` under `_meta.excluded`.

> **If a Pages site 404s, check this first.** In August 2026 an unrelated merge
> removed `.site/` and `deploy.yml` from five repositories. The organization
> portal kept linking all of them and the `gh-pages` branches were gone, so five
> cards on the front page 404'd until it was noticed by accident.

---

## Per-repository workflows

### Releasing

| Repository | Workflow | Purpose |
|---|---|---|
| `pydevices`, `palettes`, `pdwidgets`, `pygraphics`, `lvgl-python` | `publish-release-packages.yml` | The only package release coordinator. Calls the reusable workflows above. See the [runbook](publishing-automation.md). |
| `lvgl-python` | `sync-and-release.yml` | Cross-repository LVGL sync and release. The only reader of `RELEASE_WORKFLOW_TOKEN`. |
| `lvgl-bindings` | `trigger-lvgl-python-release.yml` | Dispatches the release above after bindings regenerate. |
| `lvgl-bindings` | `check-dispatch-token.yml` | `workflow_dispatch` only. A manual credential check for that cross-repo dispatch — run it when a trigger fails silently. |
| `mpftp` | `publish-vsix.yml` | Packages and publishes the VS Code extension. Not a Python distribution, so it is outside the runbook. |
| `pydevices-android-runner` | `release_apk.yml` | On `v*` tags, builds the multi-ABI Runner APK and attaches it to the GitHub Release. This is what `android.py --install-apk` downloads, so most users never build one. |

### Testing and linting

| Repository | Workflow | Notes |
|---|---|---|
| `pydevices`, `palettes`, `pdwidgets`, `pygraphics`, `pydevices-examples`, `mip` | `tests.yml` | Unit tests plus `ruff`. `pdwidgets` checks out sibling repositories first, because it imports `appdev`, `pygraphics`, and `palettes` from them. `pygraphics` runs the suite **twice** — pure Python and, with `PYGRAPHICS_TEST_NATIVE=1`, the native C extension — so the two implementations cannot drift apart again. |
| `mip` | `ruff.yml` | Lint only, separate from `tests.yml`. |
| `mip` | `commit-formatting.yml` | Enforces commit-message conventions inherited from upstream micropython-lib. |

### Validation

| Repository | Workflow | Notes |
|---|---|---|
| `pydevices`, `pygraphics` | `validate-pyscript-filesystem-toml.yml` | Thin caller of the reusable validator; rejects a stale committed TOML mapping. |
| `pydevices-examples` | `manifests.yml` | Manifest freshness for the gallery and install packages. |
| `mip` | `validate-mip-package-index.yml` | Validates the latest-only package index after a publication request lands. |

### Documentation

| Repository | Workflow | Notes |
|---|---|---|
| `palettes`, `pdwidgets`, `pygraphics` | `docs.yml` | The three ReadTheDocs library sites — the deliberate exception to the markdown-only rule. All three build with `strict: true`. See [building-docs.md](building-docs.md). |

### MIP index

| Repository | Workflow | Notes |
|---|---|---|
| `mip` | `process-mip-publication-request.yml` | Receives the serialized queue dispatch and runs the reusable synchronizer. |
| `mip` | `deploy-mip-index-to-pages.yml` | Publishes the index to Pages. Note it triggers on the **`PyDevices`** branch, not `main`. |

---

## Conventions

- **A repository in `repos_db.json` has `.site/` and a `deploy.yml`.** The only
  exceptions are the two recorded above.
- **Package releases go through the runbook**, never a bespoke per-repo release
  job. `publish-vsix.yml` and `release_apk.yml` are not Python distributions and
  are the exceptions.
- **Never edit `.site/index.html` by hand** — regenerate from the database.
- **Shared logic belongs in a `reusable-*.yml` here**, called at a stable ref, not
  copied between repositories.
