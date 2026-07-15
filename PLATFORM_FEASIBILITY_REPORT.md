# PyDisplay Platform Feasibility Report

**Date:** 2026-07-14 (analysis)  
**Triage:** 2026-07-15 — org decisions recorded below (pursue / docs-only / not-a-track / ruled out)  
**Scope:** Feasibility of extending PyDevices / PyDisplay to additional display targets beyond the current portability matrix.  
**Author:** PyDevices Cloud Agent (based on review of all owned repositories under `/home/ubuntu/gh/pydevices` and `/agent/repos`).  
**Location:** [PyDevices/.github](https://github.com/PyDevices/.github) (`PLATFORM_FEASIBILITY_REPORT.md`). Actionable workstreams: [`PLATFORM_ROADMAP.md`](PLATFORM_ROADMAP.md).

---

## Executive summary

PyDevices’ stated goal is to run **pydisplay everywhere Python runs with a usable display**. Today that is largely true for **MicroPython**, **CircuitPython**, and **CPython** across microcontrollers, Unix/Linux, Windows, the browser (PyScript/Wokwi), Jupyter, and **Android** (CPython via python-for-android). The stack is deliberately layered:

| Layer | Repos | Role |
|-------|-------|------|
| Application API | `pydisplay` (`displaysys`, `eventsys`, `graphics`, `multimer`) | Portable RGB565 display contract, unified input events, timers |
| Hardware acceleration | `displayif`, `graphics`, `usdl2` | Native C modules for bus/framebuffer interfaces, drawing, SDL2 subset |
| GUI toolkit (optional) | `lv_bindings` + `lv_*_mod` | LVGL bindings for all three Python runtimes |
| Packaging | `pydisplay_android`, TestPyPI wheels, MIP/`installer.py` | APK path and prebuilt packages |
| Build workspace | `cmods` | Optional multi-usermod MicroPython build orchestration |

**Display backends today** (`pydisplay/src/lib/displaysys/`):

| Backend | Typical target |
|---------|----------------|
| `BusDisplay` | MCU SPI/I80/I2C panels |
| `FBDisplay` | MCU/CircuitPython **panel RAM buffers** (`framebufferio`, `displayif.rgbframebuffer`, etc.) — *not* Linux `/dev/fb*` |
| `SDLDisplay` | CPython, MicroPython Unix, CircuitPython Unix, **Android** |
| `PGDisplay` | CPython desktop (PyGame CE) |
| `PSDisplay` | PyScript browser canvas |
| `JNDisplay` | Jupyter Notebook |
| `PixelDisplay` / `EPaperDisplay` | NeoPixel grids, e-paper |

### Org decisions (2026-07-15)

| Target | Feasibility | Org decision | Notes |
|--------|:-----------:|--------------|-------|
| Linux fbdev / DRM / KMS (no WM) | Medium–High | **Pursue** | SDL `kmsdrm` first; native fbdev/DRM only if needed. Parallel with other pursue tracks. Why-comments on KMS edits. |
| Android TV / Fire OS | Medium–High | **Pursue** | Phone Android treated as stable. Why-comments on new edits. |
| LG webOS / Samsung Tizen (web) | Low–Medium | **Pursue** (web only) | PyScript TV examples + remote/key bridge; **no native SDL**. Why-comments on new edits. |
| iOS / iPadOS via PyScript | Low–Medium | **Docs note only** | Position Mobile Safari / `PSDisplay` in platform docs; no dedicated smoke campaign. |
| Native iOS / iPadOS app | Low–Medium | **Ruled out** | Foreseeable roadmap: Apple path is PyScript-in-Safari (docs note) only. |
| Apple watchOS | Very Low | **Ruled out** | Entirely. |
| FreeRTOS / new MCU boards | Medium (via MP) | **Not a platform track** | Normal `displayif` + board_config product work. |
| Zephyr RTOS | Low–Medium | **Not a platform track** | Only if a specific board need appears later. |
| Nintendo Switch / Vita / PS | Very Low | **Ruled out** | Org roadmap — no consoles. |

**Parallel OK:** Linux KMS, Android TV, and webOS/Tizen web may proceed independently (no forced sequence).

**Standing rule:** Any non-obvious edit that exists **because** of KMS, Android TV, or webOS/Tizen must include a short why-comment (or adjacent doc note for config-only changes).

---

## Methodology

This report is based on:

1. README, platform docs, and source review across **all owned repos**: `pydisplay`, `pydisplay_android`, `displayif`, `graphics`, `usdl2`, `cmods`, `lv_bindings`, `lv_micropython_cmod`, `lv_circuitpython_mod`, `lv_cpython_mod`, `PyDevices.github.io`, `.github`.
2. Mapping each target to existing **display backend contracts**, **runtime availability** (MicroPython / CircuitPython / CPython), and **packaging** paths already in the ecosystem.
3. External platform constraints (store policies, official language runtimes, input modalities) where the codebase has no prior work.
4. **2026-07-15 triage** with Brad — decisions in the summary table above supersede earlier “recommended priority” wording elsewhere in this doc.

**Important naming note:** PyDisplay’s `FBDisplay` wraps **device-local scanout buffers** (CircuitPython `framebufferio`, MicroPython `displayif` RGB/MIPI modules). It is **not** a Linux kernel framebuffer (`/dev/fb0`) driver. Linux desktop targets today use **SDL2** (`SDLDisplay` + `usdl2`) or **PyGame** (`PGDisplay`), which require a display server or SDL’s platform layer—not bare fbdev/KMS directly.

---

## 1. Apple Mobile Ecosystem (iOS / iPadOS / watchOS)

### Current state in PyDevices

- **No iOS, iPadOS, or watchOS references** in pydisplay or sibling repos.
- **No MicroPython or CircuitPython port** for Apple mobile OSes.
- **CPython on iOS** is not supported by `pydisplay_android` (python-for-android targets Android only).
- Closest existing capability: **[PyScript](https://pydevices.github.io/pydisplay/pyscript/)** (`PSDisplay`) runs in **Mobile Safari** with no App Store packaging—usable display, but not a native app.

### Technical assessment

| Sub-target | Python runtime | Display path | Blockers |
|------------|----------------|--------------|----------|
| **iOS / iPadOS (native app)** | CPython possible via [BeeWare Briefcase](https://beeware.org/), [Kivy-ios](https://github.com/kivy/kivy-ios), or custom Xcode embedding; not in PyDevices today | `usdl2` / SDL2 *can* target iOS, but PyDevices has no iOS build recipes, signing, or App Store pipeline | Apple code-signing; App Store review; no JIT on iOS (affects some Python builds); SDL main-loop integration; touch-safe `multimer` backend |
| **iOS / iPadOS (web)** | PyScript / WASM asyncio | `PSDisplay` canvas | Offline/PWA limits; no full filesystem; performance vs native |
| **watchOS** | No practical CPython/MP | N/A | Screen ~200×200; no SDL; watchOS app model incompatible with pydisplay’s event loop assumptions |

### Feasibility: **Low–Medium** (iOS/iPadOS), **Very Low** (watchOS)

**Why not High:** PyDevices has invested in Android CPython (`pydisplay_android` + TestPyPI `usdl2` Android wheels). iOS would require a **parallel packaging track** (Xcode, CocoaPods/SDL, Apple Developer Program) with no shared p4a infrastructure.

**Effort estimate (native iOS):** Large — new repo, CI on macOS runners, SDL iOS glue, touch + safe-area input in `eventsys`, App Store compliance. **6+ subsystem touchpoints** (`usdl2`, `displaysys`, `multimer`, `eventsys`, packaging, LVGL wheels).

### Org decision

| Sub-target | Decision |
|------------|----------|
| **iOS / iPadOS (PyScript / Mobile Safari)** | **Docs note only** — mention in platform docs as the Apple mobile path; no dedicated smoke campaign. |
| **iOS / iPadOS (native app)** | **Ruled out** for the foreseeable roadmap. Do not start `pydisplay_ios` / macOS CI from this work. |
| **watchOS** | **Ruled out** entirely. |

---

## 2. Bare Linux Framebuffer / DRM / KMS (No Window Manager)

### Current state in PyDevices

- **Linux desktop** is supported via `SDLDisplay` / `PGDisplay` under X11 or Wayland (`pydisplay/docs/platforms/cpython-desktop.md`).
- **`FBDisplay` is MCU-oriented** — wraps RAM buffers flushed to panels via `displayif` or CircuitPython `framebufferio`, not `/dev/fb*`.
- **LVGL** (in `lv_bindings`) includes optional `LV_USE_LINUX_FBDEV` and `LV_USE_LINUX_DRM` drivers, but PyDevices’ `lv_cpython_mod/lv_conf.h` sets `LV_USE_OS` to `LV_OS_NONE` and does **not** enable Linux fbdev/DRM for pydisplay’s presentation path.
- **`usdl2`** exposes a pydisplay-sized SDL2 subset; SDL2 on Linux can use `SDL_VIDEODRIVER=kmsdrm` on many embedded boards **without a window manager**, but this is untested/documented in PyDevices.

### Technical assessment

Embedded Linux kiosks (Raspberry Pi without desktop, industrial HMI, digital signage SBCs) often need:

1. Direct scanout to `/dev/fb0` (legacy fbdev), or  
2. **DRM/KMS** via `/dev/dri/card0` (modern), or  
3. **SDL KMS/DRM backend** (reuse existing `SDLDisplay`).

| Approach | Reuses existing code | Pros | Cons |
|----------|---------------------|------|------|
| **A. SDL `kmsdrm` video driver** | `SDLDisplay`, `usdl2`, `eventsys`, `multimer._sdl2` | Smallest diff; same Python API | Needs SDL2 with KMS; input via `evdev`/SDL; dependency on SDL behavior |
| **B. New `LinuxFBDisplay` (fbdev mmap)** | `DisplayDriver` contract, `graphics` | No X11/Wayland; true bare metal feel | New C extension or ctypes; rotation/format quirks; deprecated on many distros |
| **C. New `DRMDisplay` (libdrm/GBM)** | Same | Modern, zero-copy potential with `displayif`-style thinking | Most engineering; buffer management; mode-setting |
| **D. LVGL linux fbdev/drm driver + flush shim** | `lv_cpython_mod` / `lv_micropython_cmod` | LVGL already has drivers | Bypasses pydisplay `show()` path unless integrated as backend |

### Feasibility: **Medium–High**

**Why High potential:** Target users already run **CPython or MicroPython Unix** on Linux SBCs. The **RGB565 `DisplayDriver` API** is backend-agnostic; only presentation and input differ.

**Phased approach (adopted):**

1. **Phase 0 (validation):** Document `SDL_VIDEODRIVER=kmsdrm` + `SDLDisplay` on a Pi or similar without desktop; add `board_configs/sdldisplay/linux_kms/` example config.
2. **Phase 1:** If SDL KMS is insufficient, add **`linuxfb` native module** in `displayif` or new `linuxdisplay` repo exposing mmap’d fbdev or DRM dumb buffers to `FBDisplay`-like Python wrapper.
3. **Phase 2:** Touch via Linux `evdev` → existing `eventsys` broker patterns (similar to SDL touch normalization).

**Risks:** Variable pixel format (ARGB8888 vs RGB565); DPI/scaling; concurrent VT switch; headless CI difficulty.

### Org decision: **Pursue**

- Start with **SDL `kmsdrm`** before writing fbdev/DRM from scratch.
- May run **in parallel** with Android TV and webOS/Tizen web tracks.
- **Every KMS-enabling edit** must include a short **why-comment** explaining why it is there.

---

## 3. Zephyr RTOS & FreeRTOS

### Current state in PyDevices

- **FreeRTOS** already underpins many **MicroPython MCU ports** (ESP32, STM32, RP2040, etc.) where pydisplay runs today via `BusDisplay` / `FBDisplay` + `displayif`.
- **No Zephyr-specific** board configs, `displayif` ports, or documentation.
- **LVGL** vendored in `lv_bindings` includes OS abstraction for FreeRTOS/CMSIS-RTOS2, but pydisplay’s Python layer does not select an RTOS backend—it runs **on top of** the MP/CP runtime’s scheduler.
- **CircuitPython** does not target Zephyr in the PyDevices matrix.

### Technical assessment

| RTOS | Python availability | PyDisplay fit |
|------|---------------------|---------------|
| **FreeRTOS (via MP on ESP32, etc.)** | MicroPython ports exist | **Already supported** where display hardware has board configs + `displayif` modules |
| **FreeRTOS (no Python)** | None | **Not feasible** without porting MicroPython or another embedded Python |
| **Zephyr** | [MicroPython Zephyr port](https://docs.zephyrproject.org/) exists but is niche vs ESP32/RP2 | Would need Zephyr `displayif` port (SPI/RGB drivers), frozen `pydisplay` manifest, Zephyr-specific `board_config` |
| **Zephyr + LVGL** | LVGL has Zephyr integration in upstream LVGL; PyDevices LVGL bindings are separate | Possible long-term via MP+LVGL, not pydisplay pure-Python alone |

### Feasibility

- **FreeRTOS (with MicroPython):** **Medium–High** — largely **already done** on supported chips; work is **per-board hardware enablement**, not a new OS backend.
- **Zephyr:** **Low–Medium** — depends on MicroPython Zephyr port maturity and display driver availability in `displayif`.

### Org decision: **Not a platform-expansion track**

| Target | Decision |
|--------|----------|
| **FreeRTOS / new MCU boards** | Treat as **normal product work** (`displayif` + board_configs). Do **not** list as a distinct platform-roadmap item. |
| **Zephyr** | Same — only if/when a specific board need appears; not a standing platform workstream. |

---

## 4. Nintendo Switch & PlayStation Vita / PS

### Current state in PyDevices

- **No references** to game consoles in any owned repo.
- PyDevices targets **legitimate developer paths**: open MCU boards, desktop OSes, browser, and Android APK sideloading/store.

### Technical assessment

| Platform | Python runtime | Display | Reality |
|----------|----------------|---------|---------|
| **Nintendo Switch** | Homebrew Python ports exist (e.g. community projects); no official support | Homebrew GPU APIs (nvn reverse-engineered) | Console is locked; distribution limited to homebrew; Nintendo legal/ToS constraints |
| **PlayStation Vita** | **VitaSDK** homebrew; limited Python experiments | GLES framebuffer | Tiny homebrew audience |
| **PlayStation (PS4/PS5)** | No consumer Python | Proprietary | Not viable for PyDevices open-source goals |

### Feasibility: **Very Low**

**Why:** These platforms violate the practical meaning of “everywhere Python runs” for a **mainstream open-source project**:

- No App Store / official SDK path for Python GUIs.
- Would require **bespoke C display glue** unrelated to `displayif`’s MCU bus model or SDL desktop model.
- Maintenance burden with **legal and hardware-access risk**.

### Org decision: **Ruled out**

Do **not** pursue on the org roadmap. Cloud agents must not open console/homebrew platform work from this report.

---

## 5. Android TV / Fire OS

### Current state in PyDevices

- **`pydisplay_android`** provides a **proven CPython + SDL2** path (`SDLDisplay`, `usdl2`, TestPyPI wheels).
- Android TV and **Fire OS** (Amazon’s Android fork) run standard Android APKs with adjustments for **leanback launcher**, **D-pad/remote input**, and often **no touchscreen**.
- **Phone Android is treated as stable** (2026-07-15 triage) — TV work need not wait on phone packaging.

### Technical assessment

| Concern | Status | Work needed |
|---------|--------|-------------|
| Display (SDL fullscreen) | `board_config.py` already uses `SDL_WINDOW_FULLSCREEN_DESKTOP` on Android | Verify on TV emulator (1080p/4K, overscan) |
| Input | `eventsys` maps touch to mouse-like events; key events exist | Map `KEYCODE_DPAD_*`, `KEYCODE_ENTER`, back button; optional leanback focus model |
| Packaging | `buildozer.spec` + p4a recipes | TV launcher intent category; possibly separate `pydisplay_android_tv` template |
| Fire OS | Sideload APKs; no Google Play required | Test on Fire Stick; Amazon may restrict some native libs—SDL historically OK |
| MicroPython on TV | N/A | CPython only (same as phone Android) |

### Feasibility: **Medium–High**

**Why High:** This is an **extension of existing Android work**, not a new runtime or display backend. Same `SDLDisplay` + `usdl2` + `multimer._sdl2` stack.

**Suggested first steps:**

1. Add **Android TV emulator** smoke test to `pydisplay_android/scripts/`.
2. Ship **`board_config_tv.py`** variant (focus on key/gamepad events, 10-foot UI scale).
3. Document in `pydisplay/docs/platforms/android.md` § Android TV / Fire OS.
4. Optional: PyWidgets / LVGL **focus navigation** for D-pad (larger widget effort).

**Risks:** Store policies (Play Store vs sideload); Fire OS version fragmentation; performance on low-end sticks.

### Org decision: **Pursue**

- May run **in parallel** with Linux KMS and webOS/Tizen web.
- **Every new edit** for this track must include a short **why-comment**.

---

## 6. LG webOS & Samsung Tizen

### Current state in PyDevices

- **No webOS or Tizen** native integration.
- Closest match: **browser-based PyScript** (`PSDisplay`) — both TV platforms ship **Chromium-based browsers** and encourage **web apps** for UI.

### Technical assessment

| Platform | Native Python | Practical UI stack | PyDisplay path |
|----------|---------------|-------------------|----------------|
| **LG webOS** | Not supported for consumer apps | Enact/JS, HTML5 web apps | Package PyScript static bundle; host on device browser or webOS web app manifest |
| **Samsung Tizen** | Tizen .NET/C++; HTML5 for TV apps | Tizen Web CLI | Same—hosted PyScript or WASM Python; no `SDLDisplay` |

**webOS** developer mode allows installing web apps; **Tizen** uses Samsung’s IDE and certificate signing for store distribution.

### Feasibility: **Low–Medium** (web-only), **Very Low** (native Python)

**Why not native:** Neither platform offers a **CPython or MicroPython** story comparable to Android’s p4a. Building `usdl2` for webOS/Tizen native apps would mean **platform-specific C++ app shells**—outside PyDevices’ Python-first packaging model.

**Adopted approach (web only):**

1. **Position PyScript gallery** as the TV web story—`PSDisplay` + async timers already work in Chromium.
2. Add **`web/pyscript/tv/`** examples (large fonts, remote key handling via JS bridge)—may require small **PyScript JS callbacks** for Tizen/webOS key codes.
3. Do **not** plan native `SDLDisplay` on these OSes.

### Org decision: **Pursue (web / PyScript only)**

- Native webOS/Tizen Python remains **out of scope**.
- May run **in parallel** with Linux KMS and Android TV.
- **Every new edit** for this track must include a short **why-comment**.

---

## Cross-cutting requirements

Any new platform likely needs coordinated updates across:

| Component | Repo | Notes |
|-----------|------|-------|
| Display backend | `pydisplay` `displaysys/` | New class or SDL driver env |
| Native glue | `usdl2`, `displayif`, or new repo | mmap fbdev, DRM, or platform SDL |
| Input normalization | `pydisplay` `eventsys/` | evdev, TV remote, gamepad |
| Timers | `pydisplay` `multimer/` | Must not block UI thread (see Android `_sdl2` precedent) |
| Board config | `pydisplay/board_configs/` | Per-target wiring |
| Packaging | `pydisplay_android`, static web | p4a / TV intent; no native iOS packaging track |
| LVGL (optional) | `lv_cpython_mod`, etc. | Separate display flush integration |
| Docs / CI | `pydisplay/docs/platforms/` | Headless smoke tests are hard for bare KMS |
| Why-comments | All pursue tracks | Document *why* KMS / Android TV / webOS–Tizen edits exist |

---

## Org roadmap (post-triage)

| Bucket | Targets |
|--------|---------|
| **Pursue now** (parallel OK) | Linux KMS (SDL first); Android TV / Fire OS; webOS / Tizen via PyScript |
| **Docs only** | iOS / iPadOS PyScript note in platform docs |
| **Not a platform track** | FreeRTOS board expansion; Zephyr |
| **Ruled out** | Native iOS; watchOS; Switch / Vita / PS; native webOS/Tizen |

Cloud agents: pick any **Pursue now** stream; do **not** reopen ruled-out targets from this report. Prefer [`PLATFORM_ROADMAP.md`](PLATFORM_ROADMAP.md) for concrete first steps.

---

## Conclusion

PyDevices is **well architected for portability**: the `DisplayDriver` RGB565 contract, `board_config` wiring pattern, and split between pure Python (`pydisplay`) and native acceleration (`displayif`, `graphics`, `usdl2`) make **incremental platform additions** possible without rewriting application code.

**Org focus (2026-07-15):**

1. **Bare Linux (KMS)** — SDL `kmsdrm` validation first.  
2. **Android TV / Fire OS** — extend the existing Android stack.  
3. **webOS / Tizen (web)** — PyScript TV examples + remote keys; no native shell.  
4. **Apple** — docs note for Mobile Safari only; no native iOS or watchOS.

MCU board enablement (FreeRTOS-backed MicroPython) continues as ordinary product work, not a named platform-expansion program.

---

## References (sibling repos)

Paths relative to the `pydevices/` parent (this file lives in `.github`):

| Document | Path |
|----------|------|
| PyDisplay README & portability table | `../pydisplay/README.md` |
| Platform matrix | `../pydisplay/docs/platforms/index.md` |
| Android platform notes | `../pydisplay/docs/platforms/android.md` |
| Display backend internals | `../pydisplay/docs/concepts/display-backends.md` |
| pydisplay_android README | `../pydisplay_android/README.md` |
| displayif module map | `../displayif/README.md` |
| usdl2 scope & Android wheels | `../usdl2/README.md` |
| Org overview | [`profile/README.md`](profile/README.md) |
| Platform roadmap (workstreams) | [`PLATFORM_ROADMAP.md`](PLATFORM_ROADMAP.md) |
