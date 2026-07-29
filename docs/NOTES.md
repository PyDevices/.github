# Personal notes

Brad's personal working notes for PyDevices work across sibling repos
(`pydisplay`, `cmods`, `micropython-lib`, `pydisplay_android`, etc.).
Not contributor-facing and not published via Pages or RTD — lives here
so it can sync with the org clone without being a product/docs surface.

## Todo

### Frozen & standalone apps

- [ ] Frozen self-installer for MicroPython (Unix + `micropython.exe`) — see [`docs/frozen-self-installer-notes.md`](frozen-self-installer-notes.md) *(pydisplay, micropython-lib)*
- [ ] Develop apps and freeze them into standalone executables — start with `spotapi_remote` in the spotapi repo *(spotapi — external, not a cloned sibling)*
  - Research packaging alternatives: **Electron** (JS shell + web UI) and **PyInstaller** (CPython frozen binary) vs MicroPython frozen executables; pick what fits each app
- [ ] Create a feature-accurate Minesweeper game modeled after Windows Minesweeper _(pydisplay)_
- [ ] Create a joystick emulator to run on an MCU and appear as a joystick over USB _(micropython-hardware)_
- [ ] Create a dino game to feature in the HTML of the gallery index. Fixed-height display that scales to page width; stay 1×1 (hidden) until a Dino button is pressed, equivalent to Run on `micropython.html` / `pyodide.html` _(pydisplay)_
