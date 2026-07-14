# AGENTS.md — Cloud agent workspace layout

Instructions for AI agents and humans working in the **PyDevices cloud
workspace** (Cursor Cloud Agent VM). This complements
[CONTRIBUTING.md](CONTRIBUTING.md) and [github-presence.md](github-presence.md).

On a developer laptop, repos usually live as siblings under a single parent
(e.g. `~/gh/pydevices/`). The cloud VM mirrors that layout under
`/home/ubuntu/gh/` using symlinks into `/agent/repos/`.

## Top-level layout

```
/home/ubuntu/gh/
└── pydevices/
    ├── cmods              -> /agent/repos/cmods
    ├── dotgithub          -> /agent/repos/.github   (this repo)
    ├── PyDevices.github.io -> /agent/repos/PyDevices.github.io
    ├── pydisplay          -> /agent/repos/pydisplay
    └── pydisplay_android  -> /agent/repos/pydisplay_android
```

**Not cloned locally:** `micropython-lib` — GitHub Actions owns sync and
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
├── graphics             -> /agent/repos/graphics
├── lv_bindings          -> /agent/repos/lv_bindings
├── lv_circuitpython_mod -> /agent/repos/lv_circuitpython_mod
├── lv_cpython_mod       -> /agent/repos/lv_cpython_mod
├── lv_micropython_cmod  -> /agent/repos/lv_micropython_cmod
└── usdl2                -> /agent/repos/usdl2
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
| `lv_bindings/lvgl` | Binding generator (`regenerate_*.sh`); MicroPython & CircuitPython builds (`micropython.mk`, `circuitpython.mk`) |
| `lv_cpython_mod/lvgl` | CPython extension sources (`setup.py` / TestPyPI wheels) |

**Do not maintain two separate LVGL checkouts.** Use one real tree and a
symlink:

```
lv_bindings/lvgl/              ← canonical (git submodule; pin lives here)
lv_cpython_mod/lvgl  ->  ../lv_bindings/lvgl
```

Initialize the canonical copy once:

```bash
cd /home/ubuntu/gh/pydevices/cmods
git -C lv_bindings submodule update --init --depth 1 lvgl
rm -rf lv_cpython_mod/lvgl          # only if empty placeholder
ln -s ../lv_bindings/lvgl lv_cpython_mod/lvgl
```

### LVGL reminders for agents

1. **Bump the pin in `lv_bindings` only** — `lv_cpython_mod/lvgl` follows via
   the symlink.
2. **Do not run** `git submodule update --init lvgl` inside `lv_cpython_mod`
   after symlinking — Git would replace the symlink with a second submodule
   checkout.
3. **Do not commit** the `lv_cpython_mod/lvgl` symlink as a substitute for the
   submodule gitlink; it is a local workspace convenience. CI still records
   `lvgl` as a submodule in that repo.
4. MP/CP builds read `lv_bindings/lvgl` only. Initialize it with
   `git -C lv_bindings submodule update --init --depth 1 lvgl` (see above).

## Symlink safety

When removing paths under `pydevices/` or `cmods/`, delete **symlinks only**
(`rm path` on the link), never `rm -rf` through a symlink into
`/agent/repos/*` unless the intent is to destroy an owned repo.

## Related docs

- [cmods AGENTS.md](https://github.com/PyDevices/cmods/blob/main/AGENTS.md) —
  build matrix (`build_all.sh`, `build_target.sh`, `build_mp.sh`)
- [lv_bindings PUBLISHING.md](https://github.com/PyDevices/lv_bindings/blob/main/PUBLISHING.md) —
  binding regeneration and `lv_cpython_mod` release dispatch
