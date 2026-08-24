# AGENTS.md — Cloud agent workspace layout

Instructions for AI agents and humans working in the **PyDevices cloud
workspace** (Cursor Cloud Agent VM). This complements
[CONTRIBUTING.md](CONTRIBUTING.md), [docs/github-presence.md](docs/github-presence.md),
and the shared directory convention in [docs/repo-layout.md](docs/repo-layout.md).

On a developer laptop, repos usually live as siblings under a single parent
(e.g. `~/gh/pydevices/`). The cloud VM mirrors that layout under
`/home/ubuntu/gh/` using symlinks into `/agent/repos/`.

**Automatic setup:** `.cursor/environment.json` in this repo runs
`scripts/cloud-workspace-install.sh`, `scripts/cloud-python-deps.sh`, and
`scripts/cloud-pydevices-examples-dev-env.sh` on each cloud VM boot (all idempotent).
After a successful install, agents should start real work immediately — no
separate “workspace configuration” chat.

`cloud-workspace-install.sh`:
- Creates `/agent/repos` when missing and shallow-clones any absent PyDevices
  siblings (Cursor’s `repositoryDependencies` expands GitHub token scope; it
  does not always materialize those checkouts).
- Builds `~/gh/pydevices/` symlinks, shallow-clones MicroPython/CircuitPython,
  inits `lvgl-bindings/lvgl`, and replaces an empty `lvgl-python/lvgl`
  placeholder with the canonical symlink.
- Exits non-zero if required repos or LVGL are still missing.

`cloud-python-deps.sh`:
- Installs `python3-venv` / `libsdl2-dev` via apt when the VM snapshot omits
  them, recreates broken `.venv` leftovers, then installs pydevices-examples
  (`requirements-dev.txt` + `pygame-ce` + `pydevices-lvgl`), `ruff` for
  `palettes`/`pdwidgets`, and a `pydevices_siblings.pth` so examples import
  canonical product sources from `pydevices` plus the sibling
  `palettes`, `pdwidgets`, and `pygraphics` sources.

`cloud-pydevices-examples-dev-env.sh`:
- Installs pydevices-examples `requirements.txt` (TestPyPI runtime stack for CPython).
- `micropython -m mip install`s desktop `board_config`, `palettes`, and `pdwidgets` into
  `~/.micropython/lib` (`--no-mpy -t lib -i` PyDevices index for CP-shared source
  installs; omit `--no-mpy` for MicroPython-only `.mpy` — see
  pydevices `docs/install-workflows.md`).
- Appends a `pydevices-examples-env.sh` hook to `~/.bashrc` exporting `PATH`
  (`pydevices-examples/bin`) plus `PYTHONPATH` / `MICROPYPATH` entries for
  `pydevices-examples/lib/utils` and the canonical `pydevices` product paths.
  Run examples from `pydevices-examples/lib/`.

Use the **`pydevices-cloud-handoff`** skill (`/pydevices-cloud-handoff`) when
handing work from Cursor desktop to Cloud Agents.

## Top-level layout

```
/home/ubuntu/gh/
└── pydevices/
    ├── cmods                 -> /agent/repos/cmods
    ├── dotgithub             -> /agent/repos/.github   (this repo)
    ├── pydevices  -> /agent/repos/pydevices
    ├── mpftp                 -> /agent/repos/mpftp
    ├── PyDevices.github.io   -> /agent/repos/PyDevices.github.io
    ├── palettes              -> /agent/repos/palettes
    ├── pdwidgets             -> /agent/repos/pdwidgets
    ├── pydevices-examples             -> /agent/repos/pydevices-examples
    ├── android-template     -> /agent/repos/android-template
    └── pyscript-template    -> /agent/repos/pyscript-template
```

**Not cloned locally:** `mip` — GitHub Actions owns sync and
release there; agents should not add it to this workspace unless explicitly
asked.

## `cmods` workspace interior

`pydevices/cmods` is the LVGL / native-module build workspace. Sibling repos
that also exist under `/agent/repos/` are linked in, not duplicated:

```
cmods/
├── micropython/           shallow clone @ latest stable tag (e.g. v1.28.0)
├── circuitpython/       shallow clone @ latest stable tag (e.g. 10.2.1)
├── displayif            -> /agent/repos/displayif
├── pygraphics           -> /agent/repos/pygraphics
├── lvgl-bindings          -> /agent/repos/lvgl-bindings
├── lvgl-circuitpython -> /agent/repos/lvgl-circuitpython
├── lvgl-python       -> /agent/repos/lvgl-python
└── lvgl-micropython  -> /agent/repos/lvgl-micropython
```

Upstream trees (`micropython/`, `circuitpython/`) are **read-only clones** in
this workspace — do not commit inside them (see cmods
`AGENTS.md` / `.cursor/rules/cmods-upstream-no-commit.mdc`).

### Shallow upstream clones

MicroPython and CircuitPython are intentionally small on disk until a full
build needs submodules:

```bash
git clone --depth 1 --filter=blob:none --branch <tag> --single-branch \
  https://github.com/micropython/micropython.git micropython

git clone --depth 1 --filter=blob:none --branch <tag> --single-branch \
  https://github.com/adafruit/circuitpython.git circuitpython
```

Deepen later with `git fetch --unshallow` and port-specific submodule
steps (e.g. `git -C micropython submodule update --init --recursive`,
`make -C circuitpython fetch-all-submodules` before a CP unix build).

## LVGL — one copy on disk

LVGL must be available in two places for different consumers:

| Path | Role |
|------|------|
| `lvgl-bindings/lvgl` | Binding generator (`regenerate_*.sh`); MicroPython & CircuitPython builds (`micropython.mk`, `circuitpython.mk`) |
| `lvgl-python/lvgl` | CPython extension sources (`setup.py` / TestPyPI wheels) |

**Do not maintain two separate LVGL checkouts.** Use one real tree and a
symlink:

```
lvgl-bindings/lvgl/              ← canonical (git submodule; pin lives here)
lvgl-python/lvgl  ->  ../lvgl-bindings/lvgl
```

Initialize the canonical copy once:

```bash
cd /home/ubuntu/gh/pydevices/cmods
git -C lvgl-bindings submodule update --init --depth 1 lvgl
rm -rf lvgl-python/lvgl          # only if empty placeholder
ln -s ../lvgl-bindings/lvgl lvgl-python/lvgl
```

### LVGL reminders for agents

1. **Bump the pin in `lvgl-bindings` only** — `lvgl-python/lvgl` follows via
   the symlink.
2. **Do not run** `git submodule update --init lvgl` inside `lvgl-python`
   after symlinking — Git would replace the symlink with a second submodule
   checkout.
3. **Do not commit** the `lvgl-python/lvgl` symlink as a substitute for the
   submodule gitlink; it is a local workspace convenience. CI still records
   `lvgl` as a submodule in that repo.
4. MP/CP builds read `lvgl-bindings/lvgl` only. Initialize it with
   `git -C lvgl-bindings submodule update --init --depth 1 lvgl` (see above).

## Org portal generator (`scripts/generate_sites.py`)

Generates the 16 repo/org landing pages under `../PyDevices.github.io/`
(plus `../mip/.site/` and `../pydevices-examples/.site/`) from
`data/repos_db.json` and `assets/`. Run it after editing `assets/apps/`,
`assets/css/site.css`, `assets/js/*.js`, or `repos_db.json`:

```bash
python3 scripts/generate_sites.py
```

**`assets/` is the only source of truth; deployed copies are pure sync
targets.** `_copy_chrome_into()`/`sync_assets()` copy `assets/js/*.js`,
`assets/css/site.css`, and `assets/apps/*.py` verbatim into
`PyDevices.github.io/assets/chrome/` and `PyDevices.github.io/assets/apps/`
every run. If you fix something by editing the *deployed* copy directly
(faster to iterate against a running `serve_portal.py`), that fix is
invisible to this repo and gets **silently reverted** the next time anyone
regenerates — port it back into `assets/` before you're done. This has
already happened once (a `.badge` CSS rule and a `hero-runtime.js` mip-install
fix both lived only in the deployed copy and had to be recovered from there).

**Marker-based rewrite, not merge**: every `<!-- SOMENAME: START -->` /
`<!-- SOMENAME: END -->` pair in a generated page gets its *entire* contents
replaced on each run by whatever `generate_sites.py` computes for that
marker — there is no diffing or preservation of hand edits placed *inside*
a recognized marker pair. Hand-authored content that must survive
regeneration (e.g. the "Architecture & Layers" Mermaid diagram on the portal
homepage) has to live **outside** any marker pair, not just outside the ones
you intend to touch — a new marker added to the generator later would clobber
it too if it happened to land inside. After adding hand content near a
marker, rerun the generator and diff the result before trusting it.

**Hero canvas apps** (`assets/apps/*.py`, one per repo's landing page,
executed client-side by `assets/js/hero-runtime.js`) must use the same
import shape as every other PyDevices example — `from board_config import
display_drv` + `import appdev` for raw-display apps, or `import
display_driver` + `import lvgl as lv` for LVGL apps — never construct
`WasmDisplay(...)` / `appdev.App(displays=...)` by hand. `board_config`
resolves canvas id and size from `PYDEVICES_CANVAS_ID`/`PYDEVICES_WIDTH`/
`PYDEVICES_HEIGHT` env vars that `hero-runtime.js` sets before importing the
module, and `pydevices-desktop` (the mip package `board_config` lives in) is
**not frozen** into the WASM interpreter — `hero-runtime.js` has to
`mip.install` it before the app module import can succeed. Also: both
`hero-runtime.js` and `pydevices-examples`' `gallery-host.js` just
`__import__()` the app module — there is no `main()` call — so app code must
run at module scope, not behind `if __name__ == "__main__":`, or it silently
never executes.

The 3 RTD docs sites (`palettes`, `pdwidgets`, `pygraphics` — *not* generated
by this script, see their own `docs/*.md`) embed live demos differently:
`assets/js/docs-runtime.js` `exec()`s inline `<textarea class="code-editor">`
source directly, with no `board_config` available (a docs reader has no
board file), so those snippets correctly use `displaydev.auto.AutoDisplay`
directly instead.

## Symlink safety

When removing paths under `pydevices/` or `cmods/`, delete **symlinks only**
(`rm path` on the link), never `rm -rf` through a symlink into
`/agent/repos/*` unless the intent is to destroy an owned repo.

## GitHub auth — opening PRs on sibling repos

Cloud Agents started from **`PyDevices/.github`** get an integration credential that can **push** branches into `/agent/repos/*` checkouts. When creating PRs on sibling repositories, use `gh pr create` with standard `GH_TOKEN` environment authentication:

```bash
gh pr create -R PyDevices/<repo> --base main --head <branch> --title "…" --body "…"
```

## Multi-Repository Command Iteration

See [`.agents/rules/multi_repo_command_rule.md`](../.agents/rules/multi_repo_command_rule.md)
at the workspace root — the single home for this rule.

## Known Environment Bugs

- **Checkpoints swallowing tool responses**: If an agent issues a tool call exactly as a context checkpoint fires, the response can be silently lost, causing the agent to appear hung. If this happens, ask the agent to "try again". Tracked upstream at [google-antigravity/antigravity-cli#793](https://github.com/google-antigravity/antigravity-cli/issues/793).

## Related docs

- [cmods AGENTS.md](https://github.com/PyDevices/cmods/blob/main/AGENTS.md) —
  workspace build scripts
- [lvgl-bindings releasing-bindings.md](https://github.com/PyDevices/lvgl-bindings/blob/main/docs/releasing-bindings.md) —
  binding regeneration and `lvgl-python` release dispatch
