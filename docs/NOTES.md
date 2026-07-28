# Personal notes

Brad's personal working notes for PyDevices work across sibling repos
(`pydisplay`, `cmods`, `micropython-lib`, `pydisplay_android`, etc.).
Not contributor-facing and not published via Pages or RTD — lives here
so it can sync with the org clone without being a product/docs surface.

## Todo

### LVGL

- [ ] `display_driver.py` — support multiple LVGL displays *(pydisplay)*

### displaysys & desktop

- [ ] **CircuitPython** `SDLDisplay` **forced software renderer** — `sdldisplay.py` downgrades accelerated GL on CP only (`SetRenderTarget` / `glFramebufferTexture2DEXT` fails on rotated render targets). On the same host MP unix uses SDL2 too; investigate whether this is a real CP/usdl2-binding difference or an outdated workaround — goal: HW-accelerated SDL on CP unix matching MP, or document the actual root cause *(pydisplay, cmods)*

### Frozen & standalone apps

- [ ] Frozen self-installer for MicroPython (Unix + `micropython.exe`) — see [`docs/frozen-self-installer-notes.md`](frozen-self-installer-notes.md) *(pydisplay, micropython-lib)*
- [ ] Develop apps and freeze them into standalone executables — start with `spotapi_remote` in the spotapi repo *(spotapi — external, not a cloned sibling)*
  - Research packaging alternatives: **Electron** (JS shell + web UI) and **PyInstaller** (CPython frozen binary) vs MicroPython frozen executables; pick what fits each app
