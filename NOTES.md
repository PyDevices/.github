# Personal notes

Brad's personal working notes for PyDevices work across sibling repos
(`pydisplay`, `cmods`, `micropython-lib`, `pydisplay_android`, etc.).
Not contributor-facing and not published via Pages or RTD — lives here
so it can sync with the org clone without being a product/docs surface.

## Todo



### LVGL

- [ ] Combine `display_driver.py` + `lv_utils.py` → `lv_runtime.py` *(pydisplay)*
- [ ] `lv_runtime.py` — support multiple LVGL displays *(pydisplay)*
- [ ] Ship `lv_runtime.py` with `lv_cpython_mod`, `lv_micropython_cmod`, and `lv_circuitpython_mod` *(pydisplay, cmods)*



### displaysys & desktop

- [ ] **CircuitPython** `SDLDisplay` **forced software renderer** — `sdldisplay.py` downgrades accelerated GL on CP only (`SetRenderTarget` / `glFramebufferTexture2DEXT` fails on rotated render targets). On the same host MP unix uses SDL2 too; investigate whether this is a real CP/usdl2-binding difference or an outdated workaround — goal: HW-accelerated SDL on CP unix matching MP, or document the actual root cause *(pydisplay, cmods)*
- [ ] Emulate ILI9341-style top-down (vertical) hardware scrolling in desktop `displaysys` software backends (SDL/PG/PS/JN) when `rotation` = 90 or 270 — hardware VSCRDEF/VSCSAD always scrolls top-to-bottom in the panel's native orientation, so at those rotations it should visually appear as side-to-side scrolling; software backends currently don't replicate that rotation-dependent axis flip *(pydisplay)*



### Publishing & packaging

- [x] Remove `pydisplay-bundle` everywhere — micropython-lib/MIP pruned; composite manifests removed; installer/Wokwi/docs install `displaysys`/`eventsys`/`graphics`/`multimer` individually *(pydisplay, micropython-lib)*
- [ ] Make all PyDevices repo automations that publish to TestPyPI or micropython-lib also attach those artifacts as GitHub release assets per tag — see `pydisplay/.cursor/testpypi-publish-audit.md` (gap: none do today) *(pydisplay, cmods — usdl2, graphics, lv_cpython_mod, lv_bindings)*
- [ ] `lv_cpython_mod` **tag publish (do first):** add `build_pyodide_wheel.sh` job + `gh release create` attaching cibuildwheel + `pyemscripten_2026_0` wheels (and optionally refresh Pages `wheels/` from that release) — don’t bolt Pyodide onto TestPyPI-only; then generalize release assets to the other repos above *(lv_cpython_mod, then pydisplay/cmods siblings)*
- [x] Move `pdwidgets` into its own repo and add automation to publish to TestPyPI without any examples *(pydisplay → new repo)*



### Open PRs

- [ ] `cmods#11` — esp32 displayif PSRAM preflight check. Clean/mergeable draft; triage comment left 2026-07-12. Still needs ESP32 board run of the PR checklist before undraft *(cmods)*
- [ ] `displayif#6` — active successor; draft, **CONFLICTING**, hardware test plan unchecked (Teensy 4.1, SAMD51, mimxrt1062). Triage comment left 2026-07-12 *(cmods — displayif)*

Remaining open drafts need hardware validation; `#6` also needs rebase before merge.

### Platforms & hardware

- [ ] Get `pydisplay_android` working on desktop emulator *(pydisplay_android)*
- [ ] Build MicroPython with LVGL, `graphics`, `displayif`, etc. for `board_configs/fbdisplay/esp32-p4-wifi6-touch-lcd-4b` *(pydisplay, cmods)*
- [ ] Reorganize `board_configs` if it makes sense *(pydisplay)*
- [x] PyScript PWA opening in new app with recent pushes — regression *(pydisplay)*




### Frozen & standalone apps

- [ ] Frozen self-installer for MicroPython (Unix + `micropython.exe`) — see `pydisplay/.cursor/frozen-self-installer-notes.md` *(pydisplay, micropython-lib)*
- [ ] Develop apps and freeze them into standalone executables — start with `spotapi_remote` in the spotapi repo *(spotapi — external, not a cloned sibling)*
  - Research packaging alternatives: **Electron** (JS shell + web UI) and **PyInstaller** (CPython frozen binary) vs MicroPython frozen executables; pick what fits each app



### multimer

- [ ] **multimer soft timers on librt** — reentrancy/`sleep_ms` for signal backends is improved, but on Linux CPython `hard=False` still runs callbacks in the RT signal handler: main-thread `schedule()` invokes immediately (`_schedule.py`), so soft ≈ hard for librt. `Runtime` ticks still use `hard=False`. Decide: (a) true soft — queue from signal context and drain outside the handler, or (b) document that soft only defers when delivery isn’t already on main. Test any change on librt + LVGL. *(pydisplay)*



### MCU optimization

(Multimer is out of scope for this work.)

- [ ] Optimize `lib/graphics` first, then `graphics_cmod`, for microcontrollers — memory, storage, and speed.  Floating point?  *(pydisplay, cmods — graphics)*
- [ ] Same MCU optimization pass for `eventsys` and `displaysys` (consecutively or concurrently with graphics) *(pydisplay)*



### Tooling & ecosystem

- [ ] Remove redundant and consolidate overlapping tools under `tools/`; remove any unnecessary tools that are no longer needed or used *(pydisplay)*
- [ ] Add a GUI to the matrix test kit (`tools/example_test_kit.py`) *(pydisplay)*
- [ ] Fork [figma2lvgl](https://github.com/khiyamiftikhar/figma2lvgl) and add option to output Python *(new repo — not yet created)*