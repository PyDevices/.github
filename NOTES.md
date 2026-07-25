# Personal notes

Brad's personal working notes for PyDevices work across sibling repos
(`pydisplay`, `cmods`, `micropython-lib`, `pydisplay_android`, etc.).
Not contributor-facing and not published via Pages or RTD — lives here
so it can sync with the org clone without being a product/docs surface.

## Todo

### LVGL

- [ ] `display_driver.py` — support multiple LVGL displays *(pydisplay)*
- [ ] Ship `display_driver.py` with `lv_cpython_mod`, `lv_micropython_cmod`, and `lv_circuitpython_mod` *(pydisplay, cmods)*

### displaysys & desktop

- [ ] **CircuitPython** `SDLDisplay` **forced software renderer** — `sdldisplay.py` downgrades accelerated GL on CP only (`SetRenderTarget` / `glFramebufferTexture2DEXT` fails on rotated render targets). On the same host MP unix uses SDL2 too; investigate whether this is a real CP/usdl2-binding difference or an outdated workaround — goal: HW-accelerated SDL on CP unix matching MP, or document the actual root cause *(pydisplay, cmods)*
- [ ] Emulate ILI9341-style top-down (vertical) hardware scrolling in desktop `displaysys` software backends (SDL/PG/PS/JN) when `rotation` = 90 or 270 — hardware VSCRDEF/VSCSAD always scrolls top-to-bottom in the panel's native orientation, so at those rotations it should visually appear as side-to-side scrolling; software backends currently don't replicate that rotation-dependent axis flip *(pydisplay)*

### Publishing & packaging

- [ ] Make all PyDevices repo automations that publish to TestPyPI or micropython-lib also attach those artifacts as GitHub release assets per tag — pilot `lv_cpython_mod` first (cibuildwheel + Pyodide already go to TestPyPI only). See `pydisplay/.cursor/testpypi-publish-audit.md` *(pydisplay, cmods — usdl2, graphics, lv_cpython_mod, lv_bindings)*

### Frozen & standalone apps

- [ ] Frozen self-installer for MicroPython (Unix + `micropython.exe`) — see `pydisplay/.cursor/frozen-self-installer-notes.md` *(pydisplay, micropython-lib)*
- [ ] Develop apps and freeze them into standalone executables — start with `spotapi_remote` in the spotapi repo *(spotapi — external, not a cloned sibling)*
  - Research packaging alternatives: **Electron** (JS shell + web UI) and **PyInstaller** (CPython frozen binary) vs MicroPython frozen executables; pick what fits each app

### multimer

- [ ] **multimer soft timers on librt** — on CPython + librt, soft (`hard=False`) still ≈ hard for *when* the callback runs: the backend delivers on the main thread, and `schedule()` invokes immediately there (soft coalesce/gap still apply; worker-thread backends still defer). `Runtime` ticks use `hard=False`. Decide: (a) true soft — queue from the signal handler and drain outside it, or (b) document that soft only defers when delivery isn’t already on main. Test any change on librt + LVGL. *(pydisplay)*

### MCU optimization

(Multimer is out of scope for this work.)

- [ ] Optimize `lib/graphics` first, then `graphics_cmod`, for microcontrollers — memory, storage, and speed.  Floating point?  *(pydisplay, cmods — graphics)*
- [ ] Verify `graphics-cmod` and `src/lib/graphics` parity using an MCU emulator *(cmods — graphics, pydisplay)*
- [ ] Same MCU optimization pass for `eventsys` and `displaysys` (consecutively or concurrently with graphics) *(pydisplay)*

### pdwidgets

- [ ] Agent discovery of pdwidgets interface: no `pd.Widget`-level `radius`/`text` kwarg and no `.remove()`/`.clear()` convenience — use `remove_child` (loop for full clear) and `.visible`/`.hide()`. Callbacks are always `(data_or_sender, event)`. *(pdwidgets)*

### Tooling & ecosystem

- [ ] Remove redundant and consolidate overlapping tools under `tools/`; remove any unnecessary tools that are no longer needed or used *(pydisplay)*
- [ ] Fork [figma2lvgl](https://github.com/khiyamiftikhar/figma2lvgl) and add option to output Python *(new repo — not yet created)*
