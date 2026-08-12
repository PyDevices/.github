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
| [lvgl-bindings](https://github.com/PyDevices/lvgl-bindings) | `requirements.txt` | Generator runtime (`pycparser`) |
| [pydisplay](https://github.com/PyDevices/pydisplay) | `requirements-dev.txt` | Playwright, pytest, Jupyter, ruff, … — not product runtime |
| [lvgl-python](https://github.com/PyDevices/lvgl-python) | `requirements-dev.txt` | Local editable build / wheel tooling; users install `pydevices-lvgl` |
| [pydisplay_android](https://github.com/PyDevices/pydisplay_android) | `requirements-dev.txt` | Host buildozer/Cython for APK builds — not packaged into the APK |

## Exceptions

1. **[pydisplay](https://github.com/PyDevices/pydisplay)** — example applications and gallery utilities live under `src/`. Shareable packages belong in their owning product repos, not a top-level `lib/` here.
2. **[micropython-hardware](https://github.com/PyDevices/micropython-hardware)** — canonical product repo: portable packages under `lib/`, board configs under `board_configs/`, hardware drivers under `drivers/`, and MIP manifests under `packages/`.

## Notes

- Prefer headers next to C under `src/` (not a separate top-level `include/`).
- Do not put non-unit developer tests in `tests/` — those belong in `tools/`.
- Root build glue may stay at the repo root when discovery requires it
  (e.g. `micropython.mk`, `setup.py`, `apply_*.sh` entry points).
- Meta / workspace repos (this `.github` org repo, `PyDevices.github.io`, `cmods`, `micropython-lib`) are not package trees; they follow their own roles and need not mirror every directory above.
