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
- [x] Create a patch in `cmods` to enable FFI on `micropython.exe` so it can use `uwin32.py` / hardware timers. _(cmods, multimer)_
- [x] Off-heap buffer via FFI: `uwin32` now has `VirtualAlloc` / `VirtualFree` / `buffer_at` on both the ffi and ctypes paths, and `WinDisplay._alloc_framebuffer` uses them with a `bytearray` fallback. Only WinDisplay uses it so far; SDL/PG could follow. _(pydevices, displaydev)_
- [ ] Add PyScript live examples in `palettes` and `pdwidgets`. _(palettes, pdwidgets, pydevices-examples)_


- [x] WinDisplay copies the whole framebuffer every frame: fixed, but by deleting the buffer rather than moving it off-heap. GDI reads RGB565 natively through a 16-bit `BI_BITFIELDS` DIB (`uwin32.bmi_rgb565`), so `_bgra`, the per-pixel `_rgb565_to_bgra_row` conversion loop, and the `bytes()` copy all went away together. `uwin32.dib_bits` returns a plain integer address, which both backends accept as `LPCVOID`, so nothing is marshalled per present. `_visible` went too: an unscrolled frame blits straight from `_buffer`, and a scrolled one blits it as 2-4 bands. Resident 614400 -> 153600 B (8 -> 2 B/px); MicroPython allocation 367 KB/frame -> 3.5 KB/frame; full-frame blit 6.2 -> 7076 fps (CPython) and 37 -> 7287 fps (MicroPython). _(pydevices, displaydev)_

- [x] WinDisplay allocates a new framebuffer on every rotation: fixed, but not via `_visible` -- that buffer no longer exists. `_rotate_rgb565` now rotates into a transient scratch and copies back, so `_buffer` keeps its identity (and with it the cached DIB address and the off-heap block). Steady state is 2 B/px rather than the 4 B/px that keeping `_visible` as scratch would have cost; the only allocation is the scratch, on an operation that is usually a one-off at startup. _(pydevices, displaydev)_

- [ ] WinDisplay: partial presents are disabled at fractional scales. GDI resamples each band against its own destination rectangle, so a banded repaint disagrees with a full one by 11-24 rows out of ~65 and leaves seams; `_can_band` therefore restricts banding to whole-number scales, and scrolling at a fractional scale composes into a scratch buffer first. Since `board_config` scale is routinely fitted to something fractional (2.0 -> 1.37 on this desktop), most real windows take the full-repaint path. Worth revisiting: snapping the window size so the fitted scale stays an integer would restore banding and drop the scroll scratch. _(pydevices, displaydev)_

- [ ] MicroPython ffi: passing a *long-lived* buffer to an `ffi.func` call costs ~12.5 us versus ~0.3 us for a freshly allocated one (measured on `micropython.exe` 1.28, win32, with `PeekMessageW`). Caching a MSG buffer in `WinDisplay._pump` to avoid the per-poll allocation made the pump ~20x slower, so it deliberately allocates one per poll. Worth understanding -- it inverts the usual "reuse the buffer" advice and affects every ffi-based driver. _(pydevices, uwin32)_
