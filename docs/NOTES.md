# Personal notes

Brad's personal working notes for PyDevices work across sibling repos
(`pydisplay`, `cmods`, `micropython-lib`, `pydisplay_android`, etc.).
Not contributor-facing and not published via Pages or RTD — lives here
so it can sync with the org clone without being a product/docs surface.

## Todo

### LVGL

- [ ] `display_driver.py` — support multiple LVGL displays *(pydisplay)*

### Frozen & standalone apps

- [ ] Frozen self-installer for MicroPython (Unix + `micropython.exe`) — see [`docs/frozen-self-installer-notes.md`](frozen-self-installer-notes.md) *(pydisplay, micropython-lib)*
- [ ] Develop apps and freeze them into standalone executables — start with `spotapi_remote` in the spotapi repo *(spotapi — external, not a cloned sibling)*
  - Research packaging alternatives: **Electron** (JS shell + web UI) and **PyInstaller** (CPython frozen binary) vs MicroPython frozen executables; pick what fits each app
