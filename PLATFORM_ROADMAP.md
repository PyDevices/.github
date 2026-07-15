# Platform expansion roadmap

**Triage date:** 2026-07-15  
**Repo:** [PyDevices/.github](https://github.com/PyDevices/.github)  
**Source analysis:** [`PLATFORM_FEASIBILITY_REPORT.md`](PLATFORM_FEASIBILITY_REPORT.md)

This is the **cloud-agent workstream** doc. Decisions live in the feasibility report; this file lists what to implement and what not to reopen.

Follow [AGENTS.md](AGENTS.md) for the `~/gh/pydevices` workspace layout when running as a Cloud Agent.

---

## How to use this doc (cloud agents)

1. Pick **one** pursue workstream below (tracks may run in parallel across agents/sessions).
2. Read the matching section in [`PLATFORM_FEASIBILITY_REPORT.md`](PLATFORM_FEASIBILITY_REPORT.md).
3. Implement with the **why-comment** rule on every non-obvious edit for that track.
4. Do **not** start work listed under [Out of scope](#out-of-scope) or [Not a platform track](#not-a-platform-track).

---

## Why-comment rule

Any non-obvious edit that exists **because** of Linux KMS, Android TV / Fire OS, or webOS / Tizen (web) must include a short inline comment (or an adjacent doc note for config-only changes) stating **why** that change is there — so it is not mistaken for generic cleanup.

---

## Decisions (summary)

| Bucket | Targets |
|--------|---------|
| **Pursue now** (parallel OK) | Linux KMS; Android TV / Fire OS; webOS / Tizen (PyScript only) |
| **Docs only** | iOS / iPadOS via PyScript (platform docs note; no dedicated smoke) |
| **Not a platform track** | FreeRTOS board expansion; Zephyr |
| **Ruled out** | Native iOS; watchOS; Switch / Vita / PS; native webOS / Tizen |

---

## Pursue workstreams

### 1. Linux KMS / bare framebuffer (no WM)

**Goal:** Validated pydisplay on embedded Linux without X11/Wayland, reusing `SDLDisplay` first.

**Phase 0 (do first):**

- Document and validate `SDL_VIDEODRIVER=kmsdrm` with existing `SDLDisplay` + `usdl2` on a Pi/SBC (or equivalent) without a desktop.
- Add example board config under `pydisplay/board_configs/sdldisplay/` (e.g. `linux_kms/`).
- Platform doc notes in `pydisplay/docs/platforms/` (desktop/Linux path vs KMS).

**Later (only if SDL KMS is insufficient):**

- Native fbdev mmap or DRM/GBM path (`displayif` or new module) behind a DisplayDriver-compatible wrapper — do **not** start this until Phase 0 is tried.

**Touchpoints:** `pydisplay` (`displaysys`, `board_configs`, docs), `usdl2` only if linkage/env quirks require it.

**Why-comments:** required on every KMS-enabling edit.

---

### 2. Android TV / Fire OS

**Goal:** Same CPython + SDL Android stack as phone, with TV launcher + remote/D-pad input. Phone Android is treated as **already stable** — do not block on phone work.

**First steps:**

- TV / leanback launcher intent category in `pydisplay_android` packaging (`buildozer.spec` / p4a as needed).
- `board_config` TV variant (fullscreen assumptions, 10-foot scale hints).
- Map D-pad / enter / back into `pydisplay` `eventsys` (why-comment each mapping).
- Document in `pydisplay/docs/platforms/android.md` (§ Android TV / Fire OS).
- Optional: Android TV emulator smoke under `pydisplay_android/scripts/`.

**Touchpoints:** `pydisplay_android`, `pydisplay` (`eventsys`, `board_configs`, docs), `usdl2` only if TV input/SDL gaps appear.

**Why-comments:** required on every new edit for this track.

---

### 3. LG webOS / Samsung Tizen (web / PyScript only)

**Goal:** TV web story via existing `PSDisplay` — **no** native `SDLDisplay` / platform C++ shells.

**First steps:**

- PyScript TV-oriented examples under `pydisplay/web/pyscript/` (e.g. `tv/`): large fonts, remote-friendly layout.
- JS key / remote bridge notes for webOS / Tizen key codes (why-comment bridge hooks).
- Short platform doc note: webOS/Tizen = browser/PyScript only.

**Touchpoints:** `pydisplay` (`web/pyscript`, `displaysys`/`eventsys` only if keys need normalization, docs).

**Why-comments:** required on every new edit for this track.

---

## Docs only

### iOS / iPadOS via PyScript

- Add a short note in `pydisplay` platform docs: Apple mobile = Mobile Safari + `PSDisplay` / PyScript gallery.
- **No** dedicated iPhone/iPad smoke campaign as part of this roadmap.
- Does **not** reopen native iOS packaging.

---

## Not a platform track

These are ordinary product / board enablement — not streams to open from this roadmap:

| Item | Guidance |
|------|----------|
| FreeRTOS / new MCU boards | Continue via `displayif` + `board_configs` when a board is needed. |
| Zephyr | Only if a specific board need appears later; no standing workstream. |

---

## Out of scope

Do **not** start from this roadmap:

- Native iOS / iPadOS app (`pydisplay_ios`, BeeWare/Kivy packaging, macOS CI for App Store)
- watchOS
- Nintendo Switch, PlayStation Vita, PS4/PS5 (org roadmap)
- Native webOS / Tizen Python or `usdl2` on those OS shells (web path only — see pursue #3)

---

## Related

| Doc | Role |
|-----|------|
| [`PLATFORM_FEASIBILITY_REPORT.md`](PLATFORM_FEASIBILITY_REPORT.md) | Analysis + org decisions |
| [`NOTES.md`](NOTES.md) | Brad’s personal todo (not this roadmap) |
| [`AGENTS.md`](AGENTS.md) | Cloud workspace layout |
| `pydisplay` platform docs | User-facing install/portability matrix |
