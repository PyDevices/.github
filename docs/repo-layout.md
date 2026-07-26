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
| `tests/` | Unit tests only |
| `tools/` | Developer tools and smoke / integration helpers (not maintainer publish scripts) |
| `scripts/` | Maintainer and CI scripts (publish, sync, regen) |
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
| Docs site config | `mkdocs.yml` | Yes |
| Short entry scripts | `apply_*.sh`, `build_*.sh`, `regenerate_*.sh` | Yes when they are the public entry point |
| License / community | `LICENSE`, `README.md`, `AGENTS.md`, `CONTRIBUTING.md` | Yes |
| Pip requirements | `requirements.txt`, `requirements-dev.txt` | Yes (see below) |
| Long-form docs | design notes, build guides, handoffs, publishing write-ups | No — use `docs/` |

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

MkDocs (and similar) stay under **`docs/requirements.txt`**, not at the repo
root.

Examples:

| Repo | File | Why |
|------|------|-----|
| [lv_bindings](https://github.com/PyDevices/lv_bindings) | `requirements.txt` | Generator runtime (`pycparser`) |
| [pydisplay](https://github.com/PyDevices/pydisplay) | `requirements-dev.txt` | Playwright, pytest, Jupyter, ruff, … — not product runtime |
| [lv_cpython_mod](https://github.com/PyDevices/lv_cpython_mod) | `requirements-dev.txt` | Local editable build / wheel tooling; users install `lvgl-cpython` |
| [pydisplay_android](https://github.com/PyDevices/pydisplay_android) | `requirements-dev.txt` | Host buildozer/Cython for APK builds — not packaged into the APK |

## Exceptions

1. **[pydisplay](https://github.com/PyDevices/pydisplay)** — product source lives under `src/` (including `src/lib/…` packages). Do **not** use a top-level `lib/`.
2. **[micropython-hardware](https://github.com/PyDevices/micropython-hardware)** — board configs, drivers, and MIP manifests only. No `lib/` (users install the board_config and related files they need).

## Notes

- Prefer headers next to C under `src/` (not a separate top-level `include/`).
- Do not put non-unit developer tests in `tests/` — those belong in `tools/`.
- Root build glue may stay at the repo root when discovery requires it
  (e.g. `micropython.mk`, `setup.py`, `apply_*.sh` entry points).
- Meta / workspace repos (this `.github` org repo, `PyDevices.github.io`, `cmods`, `micropython-lib`) are not package trees; they follow their own roles and need not mirror every directory above.
