# Repo layout convention

Shared on-disk layout for PyDevices source repos. Missing folders or files are
fine when unused — only create what the repo needs.

## Directories

| Directory | Meaning |
|-----------|---------|
| `.cursor/` | Cursor rules and agent notes for this repo |
| `.github/` | GitHub workflows, issue templates, Actions config |
| `.vscode/` | Editor / workspace settings committed for the team |
| `src/` | C sources and headers (native modules) |
| `lib/` | Python package source (importable package tree) |
| `tests/` | What CI runs: unit tests, interpreter tests, checks against an outside reference |
| `tests/hardware/` | Checks that need a board, run by hand on the bench |
| `tools/` | Developer tools and smoke / integration helpers (not maintainer publish scripts) |
| `scripts/` | Maintainer and CI scripts (publish, sync, regen) |
| `third_party/` | Code from other projects, one folder each, with its own license and an `ORIGIN.txt` |
| `components/` | ESP-IDF component wrappers (`idf_component.yml`) a native module needs |
| `docs/` | Documentation |
| `web/` | GitHub Pages site (or Pages-related assets) |
| `assets/` | Static assets (images, fonts, media) for docs, examples, or the site |
| `packages/` | MIP / GitHub-mip package manifests (`.json`) |

## Root files

Keep packaging, build discovery, and short entry points at the repo root.
Long-form notes and guides belong under `docs/`.

| Kind | Examples | Stay at root? |
|------|----------|---------------|
| Packaging / build metadata | `pyproject.toml`, `setup.py`, `setup.cfg`, `MANIFEST.in`, `micropython.mk`, `circuitpython.mk` | Yes — tooling discovers these at root |
| Docs site config | `.readthedocs.yaml` (`conf.py` lives in `docs/`) | Yes |
| Short entry scripts | `apply_*.sh`, `build_*.sh`, `regenerate_*.sh` | Yes when they are the public entry point |
| Build hooks for a native module | `manifest.py`, `micropython.mk`, `micropython.cmake` | Yes, at the module's root |
| License / community | `LICENSE`, `NOTICE`, `README.md`, `ROADMAP.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md` | Yes |
| Pins | `DEPENDENCIES.lock` | Yes |
| Pip requirements | `requirements.txt`, `requirements-dev.txt` | Yes (see below) |
| Long-form docs | design notes, build guides, handoffs, publishing write-ups | No — use `docs/` |

### Markdown naming

- Reserve all-caps Markdown names for conventional repository and community
  control files such as `README.md`, `ROADMAP.md`, `AGENTS.md`,
  `CONTRIBUTING.md`, `SECURITY.md`, and `CHANGELOG.md`.
- Every repository has a `ROADMAP.md`: planned enhancements and restructuring,
  written for users, one bullet of at most three lines each. Bugs and unmet
  needs stay in issues. A repository with nothing planned says so in a line,
  and its README links the file.
- **Do not add `RELEASE_NOTES.md`.** All three that existed carried a bare
  `## Unreleased` heading, never recorded a shipped version, and were linked from
  nowhere; they were deleted in August 2026. Releases use `--generate-notes`, so
  a hand-maintained file is a second source of truth that goes stale immediately.
- Name narrative and topic documents under `docs/` with lowercase kebab-case,
  for example `building-wheels.md`, `build-and-flash.md`, and
  `soft-reset-and-bring-up.md`.
- Keep generated fixtures and upstream or vendored filenames unchanged when
  renaming would create needless divergence from their source project. This
  includes MicroPython's `CODEOFCONDUCT.md`, SENML's `senml_*.md` pages, and
  vendored LVGL translations.
- Put a document in the repository that owns its subject: product architecture,
  package behavior, and driver contracts belong with `pydevices`; application
  tutorials and gallery integration belong with `gallery`; package-
  specific API documentation belongs with that package.

### `requirements.txt` vs `requirements-dev.txt`

A plain root `requirements.txt` means **runtime deps needed to run this repo’s
product** (or to run its primary tool). Use `requirements-dev.txt` for
developer / CI / host tooling.

| Name | Use for |
|------|---------|
| `requirements.txt` | Dependencies required to *run* the product or primary tool in this repo (e.g. generator needs `pycparser`) |
| `requirements-dev.txt` | Developer, CI, packaging, or host-only tools (lint, test runners, Jupyter, Playwright, buildozer, wheel/build helpers, editable `-e .` for local builds) |

Do **not** put a root `requirements.txt` that only lists tooling — that reads as
“install these to use the app,” which is misleading when the product ships via
MIP / TestPyPI / wheels / source trees instead.

Documentation tooling (Sphinx and its extensions) stays under **`docs/requirements.txt`**, not at the repo
root.

Examples:

| Repo | File | Why |
|------|------|-----|
| [lvgl-bindings](https://github.com/PyDevices/lvgl-bindings) | `requirements.txt` | Generator runtime (`pycparser`) |
| [gallery](https://github.com/PyDevices/gallery) | `requirements-dev.txt` | Playwright, pytest, Jupyter, ruff, … — not product runtime |
| [lvgl-python](https://github.com/PyDevices/lvgl-python) | `requirements-dev.txt` | Local editable build / wheel tooling; users install `pydevices-lvgl` |
| [android-template](https://github.com/PyDevices/android-template) | `requirements-dev.txt` | Host buildozer/Cython for APK builds — not packaged into the APK |
| [pyscript-template](https://github.com/PyDevices/pyscript-template) | none | Static app template; PyScript interpreter is vendored only for Pages deployment |

## Exceptions

1. **[gallery](https://github.com/PyDevices/gallery)** — example applications and gallery utilities live under `lib/` (`lib/examples/`, `lib/utils/`). Shareable packages belong in their owning product repos, not here.
2. **[pydevices](https://github.com/PyDevices/pydevices)** — canonical product repo: portable packages under `lib/`, board configs under `board_configs/`, hardware drivers under `drivers/`, and MIP manifests under `packages/`.
3. **Application templates** — `android-template` and `pyscript-template` are replaceable host shells, not product package trees.

## Native (C) modules

A native module is a folder that MicroPython's `USER_C_MODULES`, or a
manifest's `c_module()`, can point at. It lives in its own repository or
under `micropython-pydevices/modules/<name>/`. Either way it has:

- `manifest.py` containing `c_module(".")`, so a firmware manifest can
  `include()` it.
- `micropython.mk`, and `micropython.cmake` whenever a CMake port (esp32,
  rp2) can build it. Both name the same sources, apart from port-specific
  files each says it owns. A module only CMake ports build may leave out the
  `.mk`; one only Make ports build (unix, CircuitPython) may leave out the
  `.cmake`.
- CircuitPython support, where there is any, from the same `micropython.mk`,
  detected with `$(wildcard $(TOP)/py/circuitpy_mpconfig.h)`. A long
  CircuitPython block may move to `circuitpython.mk`, included from
  `micropython.mk`.
- C under `src/`. A module built for several ports keeps port code in
  `src/ports/<port>/`, each with its own build fragments, and shared code in
  `src/ports/common/`. CPython bindings, if any, go in `src/cpython/` with
  `setup.py` at the root.
- A `__revision__` attribute, set from `git describe` at build time. It is
  the only way to tell which source a board was built from.
- A `.pyi` stub, `<module>.pyi` at the module's root, for every importable
  name the module adds. The stub costs nothing on a device, and the docs'
  Reference section is generated from it.
- `examples/<module>_simpletest.py`, about one screen long.
- `tests/test_<module>.py`, run on the unix build by CI. When an independent
  implementation exists (Pillow, ffmpeg, zeroconf, the upstream C), add
  `tests/check_<module>_<reference>.py` beside it, run under CPython against
  that implementation.
- A README. In its own repository the README follows the org's six-part
  template. In `micropython-pydevices/modules/` it is the module's page: one
  sentence, the `--modules` name, the simpletest and its output, and links.

A module in `micropython-pydevices/modules/` shares that repository's
LICENSE, CONTRIBUTING, CI and issue tracker. It needs its own `ROADMAP.md`
only when it has planned work; otherwise its plans go in the root
`ROADMAP.md`, which links every module roadmap. It needs its own `NOTICE`
only when it vendors code.

### Code from other projects

There is one way to credit outside code. Vendored code goes in
`third_party/<name>/`, unchanged where possible, with the upstream license
file and an `ORIGIN.txt` naming the upstream URL, the commit, and every
change made. A root `NOTICE` lists each one, and the root `LICENSE` stays the
plain MIT template (see [Licensing](github-presence.md#licensing)), because a
license file that points elsewhere is not one tools can read.

A file that ports upstream code line by line keeps the upstream copyright
lines in its header beside ours. Code fetched at build time rather than
vendored is pinned in `DEPENDENCIES.lock`, and still named in `NOTICE` when
firmware we release contains it.

### Pins

Everything a build fetches or is tested against is pinned in one
`DEPENDENCIES.lock` per repository, which replaces `UPSTREAM` files and
one-off pin files:

```text
# <name> <clone-url> <full 40-character commit>
lvgl-bindings https://github.com/PyDevices/lvgl-bindings 0123456789abcdef0123456789abcdef01234567
```

One pin per line, `#` comments allowed. Notes on how to check a pin go in
comments above it. When a parent build overrides a module's pin, the parent's
pin wins, and the module's file says so in a comment.

## Notes

- Prefer headers next to C under `src/` (not a separate top-level `include/`).
- Board-run checks go in `tests/hardware/`; developer helpers and bench rigs
  go in `tools/`.
- Root build glue may stay at the repo root when discovery requires it
  (e.g. `micropython.mk`, `setup.py`, `apply_*.sh` entry points).
- Meta / workspace repos (this `.github` org repo, `PyDevices.github.io`, `micropython-pydevices`, `mip`) are not package trees; they follow their own roles and need not mirror every directory above. The
  modules under `micropython-pydevices/modules/` still follow
  [Native (C) modules](#native-c-modules).

## Preferred search paths (`MICROPYPATH` / `PYTHONPATH`)

On hosted interpreters — CPython, the MicroPython unix and Windows ports, CircuitPython
unix — set:

```bash
# Linux / macOS (bash)
export MICROPYPATH=".:.frozen:lib:utils:~/.micropython/lib:/usr/lib/micropython"
export PYTHONPATH=".:lib:utils"
```

```bat
REM Windows (cmd.exe)
set MICROPYPATH=.;.frozen;lib;utils;%USERPROFILE%\.micropython\lib
set PYTHONPATH=.;lib;utils
```

This mirrors the default search order on hosted interpreters and on hardware MCUs —
where `.frozen`, the user's `~/.micropython/lib`, and the system
`/usr/lib/micropython` are searched by default — while appending `.` (the current
folder), `lib/` (the local workspace), and `utils/` (shared dev tools). Custom
packages and examples then run from any directory without path conflicts, and
installing the CPython `micropython.py` compatibility shim stays harmless on
MicroPython because `.frozen` resolves first.

## Optional by design

The workflow helpers — [micropython-pydevices](https://github.com/PyDevices/micropython-pydevices)' presets,
[mpftp](https://github.com/PyDevices/mpftp), and the custom
[MIP index](https://github.com/PyDevices/mip) — are **all optional**. Stock
`make USER_C_MODULES=...`, `mpremote`, `circup`, and any standalone IDE work
unchanged.
