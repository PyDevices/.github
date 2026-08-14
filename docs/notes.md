# Personal notes

Brad's personal working notes for PyDevices work across sibling repos
(`pydevices-examples`, `cmods`, `mip`, app templates, etc.).
Not contributor-facing and not published via Pages or RTD — lives here
so it can sync with the org clone without being a product/docs surface.

## Todo

### Frozen & standalone apps

- [ ] Frozen self-installer for MicroPython (Unix + `micropython.exe`) — see [`docs/frozen-self-installer-notes.md`](frozen-self-installer-notes.md) *(pydevices-examples, micropython-lib)*
- [ ] Develop apps and freeze them into standalone executables — start with `spotapi_remote` in the spotapi repo *(spotapi — external, not a cloned sibling)*
  - Research packaging alternatives: **Electron** (JS shell + web UI) and **PyInstaller** (CPython frozen binary) vs MicroPython frozen executables; pick what fits each app
- [ ] Create a feature-accurate Minesweeper game modeled after Windows Minesweeper _(pydevices-examples)_
- [ ] Create a joystick emulator to run on an MCU and appear as a joystick over USB _(pydevices)_
- [ ] Create a dino game to feature in the HTML of the gallery index. Fixed-height display that scales to page width; stay 1×1 (hidden) until a Dino button is pressed, equivalent to Run on `micropython.html` / `pyodide.html` _(pydevices-examples)_
- [ ] Verify that FINGERMOTION isn't needed _(pydevices-examples)_
- [ ] After merging `multimer-selection`: fix Linux piano / `utils/audio.py` growing latency under glissando (notes start a bit late, then delay lengthens until the queue backs up badly). Windows PE was fine; all three Linux desktop runtimes showed it. Likely the wall-clock look-ahead / catch-up pump interacting with main-thread redraw — not introduced by multimer-selection (`audio.py` unchanged since `145f4475`). Context tasks: `164d87be-1a25-46a2-a2c6-fc4f4a81742a` and `768842b6-88cc-4584-99f0-b28fe4ef08e4`. _(pydevices-examples)_
- [ ] Hinch GUI trio (`nano` / `micro` / `touch_gui_simpletest`) and `widgets_locker_kiosk` still out of the example matrix — revisit and get them green (or keep parked with a clear reason). _(pydevices-examples)_
- [ ] Enable Mermaid rendering on RTD sites — ` ```mermaid ` blocks currently show as plain text, not diagrams. At least: pydevices-examples, pdwidgets, palettes, pygraphics. _(pydevices-examples, pdwidgets, palettes, pygraphics)_
- [ ] Publish more / all of pydevices to micropython-lib. _(pydevices, micropython-lib)_
- [ ] Make timer selection pattern match the established pattern in `displaydev` and `audiodev` for consistency. _(pydevices, multimer)_
- [ ] Create a patch in `cmods` to enable FFI on `micropython.exe` so it can use `uwin32.py` / hardware timers. _(cmods, multimer)_
- [ ] Add PyScript live examples in `palettes` and `pdwidgets`. _(palettes, pdwidgets, pydevices-examples)_


