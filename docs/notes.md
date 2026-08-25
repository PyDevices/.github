# Personal notes

Brad's personal working notes for PyDevices work across sibling repos
(`pydevices-examples`, `cmods`, `mip`, app templates, etc.).
Not contributor-facing and not published via Pages or RTD — lives here
so it can sync with the org clone without being a product/docs surface.

## Todo

### WebAssembly runtime

- [ ] Evaluate worker execution for the direct MicroPython WebAssembly host after the main-thread bridge and browser migrations are stable. Define framebuffer, input, audio, timer, and Python-buffer ownership across the worker boundary before implementation. _(cmods, pydevices, dotgithub)_
- [ ] Stop installing `pydevices-desktop` over the network at simulator boot, once its contents stabilize (`audiodev` is being reworked as of 2026-08-25). Both the PyDevices.github.io simulator and Workbench currently run `mip.install("pydevices-desktop", index="https://PyDevices.github.io/mip", target="lib")` on every VM boot: measured at **56 requests** (1 manifest + 55 `.mpy` files) and most of the ~20 s connect. The Emscripten FS is in-memory, so it survives a soft reset but not a page reload — every fresh session re-downloads all 56, and there is no offline path despite both apps shipping as installable PWAs. Two ways out, either is fine: **freeze the modules into the wasm build** (they join `lvgl`, `palettes`, `pygraphics`, `displaydev`, already frozen), or **ship a build-time tarball** — ViperIDE already has that machinery in Workbench, `gen_tar` in `build.py` plus `loadVFS`, as used for `vm_vfs.tar.gz` and `tools_vfs.tar.gz`. Freezing is the smaller runtime; the tarball keeps the package updatable without a wasm rebuild. Either also pins a known version, where the live index means the simulator silently changes whenever the index does. _(pydevices, cmods, workbench, PyDevices.github.io)_

### Frozen & standalone apps

- [ ] Frozen self-installer for MicroPython (Unix + `micropython.exe`) — see [`docs/frozen-self-installer-notes.md`](frozen-self-installer-notes.md) *(pydevices-examples, micropython-lib)*
- [ ] Develop apps and freeze them into standalone executables — start with `spotapi_remote` in the spotapi repo *(spotapi — external, not a cloned sibling)*
  - Research packaging alternatives: **Electron** (JS shell + web UI) and **PyInstaller** (CPython frozen binary) vs MicroPython frozen executables; pick what fits each app
- [ ] Create a feature-accurate Minesweeper game modeled after Windows Minesweeper _(pydevices-examples)_
- [ ] Create a joystick emulator to run on an MCU and appear as a joystick over USB _(pydevices)_
- [ ] Create a dino game to feature in the HTML of the gallery index. Fixed-height display that scales to page width; stay 1×1 (hidden) until a Dino button is pressed, equivalent to Run on `micropython.html` / `pyodide.html` _(pydevices-examples)_
- [ ] Verify that FINGERMOTION isn't needed _(pydevices-examples)_
- [x] Piano audio latency/glissando degradation, root-caused 2026-08-25: `audioif`'s `audiocore.get_buffer()` returned a typed (`'h'`) memoryview whose `len()` is the *sample* count, while `audiodev.sample_out.AudioOut`'s pump did byte math on it — under-counting 16-bit PCM by 2x and producing at twice realtime forever, saturating the SDL transport (500ms blocking writes, stall recycles) on desktop; I2S's blocking write happened to absorb it on the P4. Fixed in `audioif` (byte view) and the CP oracle patch, with a self-calibrating fallback in `AudioOut` for stale frozen firmware. Also added: a backpressure-aware pump (a primed/stalled transport's backlog now drains instead of riding ahead of every note forever) and tighter "low"-latency profiles. `utils/audio.py`/`AudioEngine` retired entirely (see below). Released as pydevices 0.3.4-0.3.6. _(pydevices, cmods/audioif, pydevices-examples)_
- [x] `pydevices-examples/lib/utils/audio.py` (`AudioEngine`) retired: `piano.py` and `widgets_locker_kiosk.py` (its last consumer) migrated to `synthio.Synthesizer` + `audiodev.sample_out.AudioOut`. _(pydevices-examples)_
- [x] `windisplay` pointer coordinates were double-scaled (wndproc mapped by `_scale`, then the appdev pointer pipeline divided by `touch_scale` again) — zero error at the window origin, growing with distance (~4 white keys off at the far end of the piano keyboard at scale 1.37). `touch_scale` now stays 1.0 on `WinDisplay`, matching `SDLDisplay`'s contract. _(pydevices, displaydev)_
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

### ESP32-P4 display

- [ ] pygraphics text draws (`Draw.text`/`text16`) are drastically slow on the P4's `FBDisplay` framebuffer (~1.8s for one `text16` call, measured 2026-08-25) and any `multimer`/`appdev` timer that fires *during* such a draw hard-wedges the board -- unreachable over serial, needs a hard reset. Minimal repro (mpftp `probe`): `app.every(40, noop)` + a `pygraphics.Draw` on `board_config.display_drv` + `.text16(...)`; `fill_rect` alone is fast and safe, `text`/`text16` alone (no timer) is slow but doesn't wedge, the *combination* wedges. This blocked getting `pydevices-examples/piano.py` running on the P4 -- audio itself (synthio -> AudioOut -> ES8311, verified separately via a staged diagnostic) is not implicated. Likely suspects: a per-pixel PSRAM access pattern in the text blit colliding with whatever IRQ multimer's esp32 timer uses. Repro scripts are in that session's scratchpad (`piano_interactive_probe*.py`, `p4_piano_diag*.py`). _(pydevices, pygraphics, displayif, multimer)_

### mpftp + simulator unification

- [ ] Bring the mpftp local PWA (`ui/` — file transfer + REPL, connects to real hardware over serial) and the PyDevices.github.io simulator (`simulator/` — Monaco editor + MicroPython WebAssembly + xterm REPL, runs in-browser with no board) under one shared interface. As of 2026-08-24 the mpftp PWA was deliberately reskinned to match the simulator's layout and theme (editor left, device-stage-equivalent top right, REPL bottom right; same dark navy / orange-accent palette, Space Grotesk + JetBrains Mono, draggable splitters) specifically to make this merge easier later, but the merge itself was explicitly out of scope for that pass. Open question to resolve when this is picked up: one codebase with a "target" toggle (real board over WS vs. in-browser WASM VM) sharing the editor/REPL/file-panel components, vs. two codebases that just share a design system. _(mpftp, PyDevices.github.io)_

### Firmware & flashing

- [ ] `mpftp firmware flash --uf2` — flash an already-built UF2 by copying it to the bootloader volume, instead of a serial write. Scope it to *flashing existing UF2 output*, not wrapping arbitrary binaries with `uf2conv.py`. mpftp already has both halves: `_find_circuitpy_host_roots()` for volume discovery and a working `bootloader` command. Two hard requirements: **mandatory post-copy verification** (PowerShell `Copy-Item` fails non-terminatingly — rc=0 with nothing written, which for a flash operation makes "succeeded" and "wrote nothing" indistinguishable), and a re-enumeration wait after the copy. Gate the whole path on actually detecting a bootloader volume. _(mpftp)_
- [ ] Make an ESP32-S3 board UF2-capable after it was flashed with esptool. Viable, but it is a **one-time destructive provisioning step**, not a per-build option — see below. _(mpftp, cmods)_

#### ESP32-S3 UF2: how it actually works

On S3, UF2 is not in ROM and is not a bootloader in the RP2040 sense. **tinyuf2 is an ordinary ESP-IDF app** living in the `factory` partition; CircuitPython is demoted to `ota_0`. The IDF second-stage bootloader boots factory when `otadata` is blank, and tinyuf2 then chooses between presenting the drive and chaining to the app.

`UF2_BOOTLOADER` in `ports/espressif/Makefile` does exactly one thing — pick a partition table. It defaults to `CIRCUITPY_USB_DEVICE`, so every S3 board with native USB already gets the UF2 layout:

| | with UF2 | no UF2 |
|---|---|---|
| `ota_0` | 0x010000, 2048K | 0x010000, 2048K |
| `ota_1` | 0x210000, 2048K | 0x210000, 2048K |
| `uf2` (app, **factory**) | 0x410000, 256K | — |
| user fs (fat) | 0x450000, **3776K** | 0x410000, **4032K** |

tinyuf2's own release partition table is **byte-identical** to CircuitPython's `partitions-8MB.csv` (only the fat partition's name differs, `ffat` vs `user_fs` — irrelevant, since `supervisor/internal_flash.c` looks it up by type/subtype with a `NULL` label). The two projects are designed to interlock.

Steps on an already-esptool'd board:

1. Get a tinyuf2 build for the **exact** board — separate repo (`adafruit/tinyuf2`), not vendored in CircuitPython. Prebuilt zips exist for ~14 S3 boards; otherwise add a board definition there (flash size, PSRAM, status LED pins).
2. Match the flash size. The devkitc build is 8MB; a 4MB S3 uses `partitions-4MB-no-ota.csv`, which drops `ota_1` entirely to make room.
3. Flash tinyuf2's four files (from its `flash_args`) — or its `combined.bin` at 0x0:
   ```
   0x0      bootloader.bin
   0x8000   partition-table.bin
   0xe000   ota_data_initial.bin   # this is what says "boot factory"
   0x410000 tinyuf2.bin
   ```
4. Rebuild CircuitPython with `UF2_BOOTLOADER=1` so it targets the matching layout and `make` emits `firmware.uf2` (family ID `0xc47e5767` for S3, base 0x0 — relative to the ota partition).

**The cost:** repartitioning destroys the CIRCUITPY filesystem — the fat partition moves and shrinks by 256K, and there is no in-place upgrade path. This is the opposite of RP2040, where a UF2 reflash *preserves* the filesystem. On a 4MB S3 the storage cut is 1216K -> 960K (21%), which is why `espressif_esp32s3_lcd_ev` and `..._v1.5` both set `UF2_BOOTLOADER = 0`.

**What it buys:** software-triggered bootloader entry — `microcontroller.on_next_reset(RunMode.UF2)` sets reset-reason hint `0x11F2` (`APP_REQUEST_UF2_RESET_HINT`), which survives reset; plus double-tap reset if the tinyuf2 board def enables it.

**What it does not buy:** recoverability. Unlike the RP2040 1200-baud touch — handled in the USB stack, and the thing that rescued the wedged board on 2026-08-20 — setting the hint requires the running VM to execute code. A badly wedged S3 still means holding BOOT and using esptool. So this is convenience, not a rescue path, and mpftp still needs esptool on ESP32 regardless.
