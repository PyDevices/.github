# Release workflows: inputs, secrets and tags

The release chain's moving parts, as tables. How they fit together is in
[the release chain](../how-it-works/release-chain.md).

## What each repository publishes

| Source repository | TestPyPI | MIP index |
|---|---|---|
| `pydevices` | `pydevices` (all of `lib/`) and `pydevices-desktop` | `pydevices` |
| `pygraphics` | `pydevices-pygraphics`: Linux, Windows, Android and WASM wheels | pure-Python `pygraphics` |
| `audiodsp` | `omnipython-audiodsp`: Linux, Windows, macOS, Android and WASM wheels | nothing; the native modules are firmware, built from the usermod source |
| `audiocomponents` | `pydevices-audioinstruments` and `pydevices-audioeffects`, pure Python, from one repository | `audioinstruments` and `audioeffects` |
| `omnipython-lvgl` | `pydevices-lvgl`: Linux, Windows, Android and WASM wheels | nothing |
| `mpftp` | `pydevices-mpftp` wheel and sdist | nothing |

The `palettes` and `pdwidgets` folders of `pydevices` publish separately, on
`palettes-vX.Y.Z` and `pdwidgets-vX.Y.Z` tags, to TestPyPI and the library
index. The library index (`PyDevices/lib`) takes every release of every
repository that asks it, pre-releases included.

pip distribution names carry a prefix (`pydevices-` or `omnipython-`); MIP
package names don't. `pydevices` and `pydevices-desktop` keep the same name in
both. `mpftp` also publishes its VS Code extension with `publish-vsix.yml`,
outside this chain.

## Inputs of `reusable-publish-release-packages.yml`

| Input | Meaning |
|---|---|
| `build-kind` | `pure-python`, `native-and-wasm` or `pydevices-multi`; exactly one build runs |
| `distribution-name` | The TestPyPI distribution name |
| `import-name` | `pure-python` only: the module the smoke test imports |
| `wheel-filename-prefix` | `native-and-wasm` only, for example `pydevices_pygraphics` |
| `expected-wheel-count` | `native-and-wasm` only; `0` accepts any non-empty wheel set |
| `install-dependencies` | `pure-python` only: install dependencies before the smoke test |
| `checkout-submodules` | Check out submodules before building |
| `mip-profile` | A synchronization profile, or a comma-separated list when a repository publishes several packages; empty skips MIP and the library index |
| `release-ref` | An exact `vX.Y.Z` tag, for a `workflow_dispatch` retry; empty on a release event |
| `working-directory` | `pure-python` only: the directory with `pyproject.toml` |
| `pypi-publish` | Mark final releases for production PyPI; see [publish to production PyPI](../guides/publish-to-pypi.md) |

A typical call:

```yaml
jobs:
  publish:
    uses: PyDevices/.github/.github/workflows/reusable-publish-release-packages.yml@publishing-vN
    with:
      build-kind: pure-python          # or native-and-wasm, pydevices-multi
      distribution-name: pydevices-palettes
      import-name: palettes
      mip-profile: palettes            # omit to skip MIP
      release-ref: ${{ inputs.release-ref }}
    secrets: inherit
```

## Secrets

| Secret | Where | Purpose |
|---|---|---|
| `PYDEVICES_APP_ID`, `PYDEVICES_APP_PRIVATE_KEY` | Every publishing repository and `PyDevices/mip` | Mint short-lived GitHub App tokens: to open release PRs, create tags and Releases (so `on: release` fires), dispatch the MIP queue and send the Release Health report |
| `TESTPYPI_API_TOKEN` | Every repository that uploads to TestPyPI | API token for TestPyPI |
| `VSCE_PAT`, `OVSX_PAT` | `mpftp` only (`publish-vsix.yml`) | VS Marketplace and Open VSX; both optional, the steps skip when unset |

TestPyPI uses token authentication (`user: __token__`, the token as the
password, `repository-url: https://test.pypi.org/legacy/`,
`skip-existing: true`), not Trusted Publishing. Production PyPI uses Trusted
Publishing; see [publish to production PyPI](../guides/publish-to-pypi.md).

## Tags

`publishing-vN` tags carry the reusable workflows. They're immutable: a tag
ruleset named "publishing tags are immutable" blocks moving or deleting one.
Cut a new one with `scripts/cut_publishing_tag.sh N` from a clean `main`.

There's no single current tag; each caller sits on the tag it was last moved
to. To see which, in a clone of a repository:

```bash
grep -rn "PyDevices/\.github.*@publishing" .github/workflows
```

`git ls-remote --tags https://github.com/PyDevices/.github 'publishing-v*'`
lists every tag. `mip` keeps its tools-ref in two places
(`process-mip-publication-request.yml` and `deploy-mip-index-to-pages.yml`);
move them together, because the deploy workflow rebuilds every package and an
older tools ref overwrites what a publication wrote.

## Tag history to know

- **Never pin `publishing-v10`.** It called its sibling workflows by `./`
  path, which resolves against the consumer's repository, so a consumer's run
  died at startup with no jobs ([.github#47](https://github.com/PyDevices/.github/issues/47)).
  `publishing-v11` and later name the siblings by full path at the tag's own
  name.
- **`publishing-v9` and earlier** name an older tag in their own sibling
  references, so a caller on one runs that older tag's builders. For a retry
  against v9 or earlier, check the nested references first.
- **`publishing-v11`** carries the version-grammar guard before tagging, the
  `## Unreleased` heading converted by the release PR, a release-health push
  that re-folds instead of losing a report, and the MCU split of the MIP
  packages. Its `publishing-tools-ref` defaults still name v6, which is
  harmless because the scripts are identical.
- **`publishing-v14`** added `top-level = true` sections to `mip-split.toml`.
  **`publishing-v15`** added the library-index request. Every tag from
  `publishing-v1` still exists, so a release cut before a contract change can
  be retried against the contract it was built with.
