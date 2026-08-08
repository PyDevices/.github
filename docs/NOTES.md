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
- [ ] Verify that FINGERMOTION isn't needed _(pydisplay)_
- [ ] After merging `multimer-selection`: fix Linux piano / `utils/audio.py` growing latency under glissando (notes start a bit late, then delay lengthens until the queue backs up badly). Windows PE was fine; all three Linux desktop runtimes showed it. Likely the wall-clock look-ahead / catch-up pump interacting with main-thread redraw — not introduced by multimer-selection (`audio.py` unchanged since `145f4475`). Context: [multimer-selection / piano queue](164d87be-1a25-46a2-a2c6-fc4f4a81742a), [Piano / portable audio](768842b6-88cc-4584-99f0-b28fe4ef08e4). _(pydisplay)_
- [ ] Hinch GUI trio (`nano` / `micro` / `touch_gui_simpletest`) and `widgets_locker_kiosk` still out of the example matrix — revisit and get them green (or keep parked with a clear reason). _(pydisplay)_
