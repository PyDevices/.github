# Frozen self-installer notes

Private design scratchpad (not for RTD). Org-level notes; implementation
touches pydevices-examples + micropython-lib (+ desktop MicroPython freeze).

## Todo

- [ ] Warn users where downloads come from: PyDevices mip MIP index (`https://PyDevices.github.io/mip`), not the [official MicroPython micropython-lib](https://github.com/micropython/micropython-lib) package index — **maintainer-published**, not an endorsed upstream source (show URL on first run / in GUI)
- [ ] Freeze a small bootstrap module into desktop MicroPython builds so `from <xyz> import <clever_install_fn>` works out of the box
- [ ] Install or refresh all 3 core modules (`displaydev`, `eventsys`, `pygraphics`, `multimer`) via `mip` / `lib_install`-style fetch (skip re-download when up to date?)
- [ ] Post-install GUI (TBD: terminal menu vs minimal on-display UI): download more files, system/platform info, `lv_test_timer_*`-style sanity checks, link to `spotapi_remote` / spotapi
- [ ] Flesh out scope, module name, and UX (name the import, entry points, error handling offline)

**Goal:** One-liner onboarding on MicroPython Unix and `micropython.exe` without requiring users to copy `installer.py` manually first.

**Bootstrap API (draft):**

```python
from <xyz> import <clever_install_fn>  # name TBD
<clever_install_fn>()  # fetch or refresh core libs, then optional GUI
```

**What gets installed first:** The four `src/lib` packages only — `displaydev`, `eventsys`, `pygraphics`, `multimer`. Add-ons, examples, and board configs stay optional later steps.

**Source of truth:** Maintainer-published packages from the PyDevices mip fork, published via pydevices-examples [`scripts/publish_sync_packages.sh`](https://github.com/PyDevices/pydevices-examples/blob/main/scripts/publish_sync_packages.sh) → MIP index at `https://PyDevices.github.io/mip`. Same channel as [`installer.py`](https://github.com/PyDevices/pydevices-examples/blob/main/installer.py) `lib_install()` ([installation/mip-micropython-lib.md](https://github.com/PyDevices/pydevices-examples/blob/main/docs/installation/mip-micropython-lib.md) describes the index; this installer should **warn explicitly** that it is not the official MicroPython micropython-lib registry).

**Suggested first-run warning (UI copy):**

> Installing from PyDevices mip (maintainer-published community index).  
> Not the official MicroPython package registry.  
> Index: `https://PyDevices.github.io/mip`

**Post-install GUI ideas (pick subset for v1):**

| Area | Ideas |
|------|--------|
| More packages | `utils`, `examples`, `board_config.py`, `path.py`, board_configs, display/touch drivers |
| System info | Platform, `sys.implementation`, free memory, display backend detected, timer backend (`Timer` vs `AsyncTimer`) |
| Diagnostics | Run or launch patterns like `lv_test_timer_no_pump` / `lv_test_timer_pump` / `lv_test_timer_async` / harness — platform labels, timer tick, optional touch |
| Integrations | Deep link or install hook for `spotapi_remote` / spotapi (`src/examples/spotapi` is local-only symlink today) |
| Maintenance | Refresh core libs, show installed versions, clear and reinstall |

**Existing code to reuse / align with:**

- [pydevices-examples `installer.py`](https://github.com/PyDevices/pydevices-examples/blob/main/installer.py) — `lib_install()` vs `repo_install()` split
- [pydevices-examples `scripts/publish_sync_packages.sh`](https://github.com/PyDevices/pydevices-examples/blob/main/scripts/publish_sync_packages.sh) — what actually lands on the MIP index
- Desktop `board_config` in [pydevices `board_configs/desktop/board_config.py`](https://github.com/PyDevices/pydevices/blob/main/board_configs/desktop/board_config.py) — likely still needed after core install

**Open questions:**

- Frozen module lives in pydevices-examples repo vs MicroPython port tree?
- Idempotent refresh: version manifest, etag, or always pull?
- GUI toolkit on desktop MCU port: `pdwidgets`, plain print menu, or SDL text UI?
- Relationship to future TestPyPI / pip path for CPython Jupyter (separate track)
