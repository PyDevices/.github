# Platform expansion roadmap

**Triage date:** 2026-07-15  
**Repo:** [PyDevices/.github](https://github.com/PyDevices/.github)

This is the **cloud-agent workstream** doc. It carries the org's platform-expansion
decisions directly (the original feasibility-analysis writeup that produced them
was a one-time 2026-07-14 research doc, superseded by the 2026-07-15 triage below
and since removed — this file is now the source of record for what to implement
and what not to reopen).

Follow [AGENTS.md](../AGENTS.md) for the `~/gh/pydevices` workspace layout when running as a Cloud Agent.

---

## How to use this doc (cloud agents)

1. Pick **one** pursue workstream below (tracks may run in parallel across agents/sessions).
2. Read the matching workstream section below for scope and first steps.
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
| **Docs only** | PWA (installable PyScript — **where they run**); iOS / iPadOS via PyScript |
| **Not a platform track** | FreeRTOS board expansion; Zephyr |
| **Ruled out** | Native iOS; watchOS; Switch / Vita / PS; native webOS / Tizen |

## Decisions (per target, 2026-07-15 triage)

| Target | Feasibility | Org decision | Notes |
|--------|:-----------:|--------------|-------|
| Linux fbdev / DRM / KMS (no WM) | Medium–High | **Pursue** | SDL `kmsdrm` first; native fbdev/DRM only if needed. Parallel with other pursue tracks. Why-comments on KMS edits. |
| Android TV / Fire OS | Medium–High | **Pursue** | Phone Android treated as stable. Why-comments on new edits. |
| LG webOS / Samsung Tizen (web) | Low–Medium | **Pursue** (web only) | PyScript TV examples + remote/key bridge; **no native SDL**. Why-comments on new edits. |
| iOS / iPadOS via PyScript | Low–Medium | **Docs note only** | Position Mobile Safari / `PSDisplay` in platform docs; no dedicated smoke campaign. |
| Progressive Web Apps (PyScript) | N/A (ships today) | **Docs only** | Major pydevices-examples feature — document **where PWAs run** (browser×OS×install UX) in platform docs; how-to already in `guides/pyscript-pwa.md`. |
| Native iOS / iPadOS app | Low–Medium | **Ruled out** | Foreseeable roadmap: Apple path is PyScript-in-Safari (docs note) only. |
| Apple watchOS | Very Low | **Ruled out** | Entirely. |
| FreeRTOS / new MCU boards | Medium (via MP) | **Not a platform track** | Normal `displayif` + board_config product work. |
| Zephyr RTOS | Low–Medium | **Not a platform track** | Only if a specific board need appears later. |
| Nintendo Switch / Vita / PS | Very Low | **Ruled out** | Org roadmap — no consoles. |

**Parallel OK:** Linux KMS, Android TV, and webOS/Tizen web may proceed independently (no forced sequence).

---

## Pursue workstreams

### 1. Linux KMS / bare framebuffer (no WM)

**Goal:** Validated pydevices-examples on embedded Linux without X11/Wayland, reusing `SDLDisplay` first.

**Phase 0 (do first):**

- Document and validate `SDL_VIDEODRIVER=kmsdrm` with existing `SDLDisplay` + `usdl2` on a Pi/SBC (or equivalent) without a desktop.
- Validate the canonical `pydevices/board_configs/desktop/` config under KMS; add a specialized host config there only if environment selection is insufficient.
- Platform doc notes in `pydevices-examples/docs/platforms/` (desktop/Linux path vs KMS).

**Later (only if SDL KMS is insufficient):**

- Native fbdev mmap or DRM/GBM path (`displayif` or new module) behind a DisplayDriver-compatible wrapper — do **not** start this until Phase 0 is tried.

**Touchpoints:** `pydevices` (`displaydev`, desktop config, `pydevices-desktop`) and `pydevices-examples` (examples/docs).

**Why-comments:** required on every KMS-enabling edit.

---

### 2. Android TV / Fire OS

**Goal:** Same CPython + SDL Android stack as phone, with TV launcher + remote/D-pad input. Phone Android is treated as **already stable** — do not block on phone work.

**First steps:**

- TV / leanback launcher intent category in `pydevices-android-template` packaging (`buildozer.spec` / p4a as needed).
- Android TV host settings (fullscreen assumptions, 10-foot scale hints); extend the canonical desktop config only if needed.
- Map D-pad / enter / back through the neutral PyDevices input contracts in `pydevices` (why-comment each mapping).
- Document in `pydevices-examples/docs/platforms/android.md` (§ Android TV / Fire OS).
- Optional: Android TV emulator smoke under `pydevices-android-template/scripts/`.

**Touchpoints:** `pydevices-android-template`, `pydevices` (portable input/config packages), and `pydevices-examples` (examples/docs); TestPyPI `pydevices-desktop` changes only if TV input/SDL gaps appear.

**Why-comments:** required on every new edit for this track.

---

### 3. LG webOS / Samsung Tizen (web / PyScript only)

**Goal:** TV web story via existing `PSDisplay` — **no** native `SDLDisplay` / platform C++ shells.

**First steps:**

- PyScript TV-oriented examples under `pydevices-examples/web/pyscript/` (e.g. `tv/`): large fonts, remote-friendly layout.
- JS key / remote bridge notes for webOS / Tizen key codes (why-comment bridge hooks).
- Short platform doc note: webOS/Tizen = browser/PyScript only.

**Touchpoints:** `pydevices-examples` (`web/pyscript`, examples/docs) and `pydevices` only if portable key normalization must change.

**Why-comments:** required on every new edit for this track.

---

## Docs only

### Progressive Web Apps (PWA) — major pydevices-examples feature

**Goal:** Treat installable / offline PyScript apps as a **first-class** platform story, documented as clearly as MCU / desktop / Android APK — especially **where** a pydevices-examples PWA actually runs.

Today the how-to lives in `pydevices-examples/docs/guides/pyscript-pwa.md` (manifest, service worker, COI, GitHub Pages). What is still thin: elevating PWAs in **platform** docs and spelling out the host matrix (browser × OS × install UX).

**First steps:**

- Expand `pydevices-examples/docs/platforms/` so the portability matrix and PyScript notes call out **installable PWA** alongside in-browser demos (link the existing guide; do not bury it as a gallery-only tip).
- Document a clear **where PWAs run** matrix, including at least:
  - Desktop Chromium (Chrome / Edge) — install prompt / standalone window
  - Android Chrome — install / home-screen; contrast with native `pydevices-android-template` APK
  - iOS / iPadOS Safari — Share → Add to Home Screen (no `beforeinstallprompt`)
  - Chromebook and other desktop Linux browsers as relevant
  - Relation to TV **web** path (webOS / Tizen Chromium browsers — browser or installable web app, not native SDL)
- Clarify standalone vs tab behavior, offline/cache expectations, and install UX differences per host.
- Keep implementation detail in the PWA how-to; **platform docs own “where it runs.”**

**Touchpoints:** `pydevices-examples` (`docs/platforms/`, `docs/guides/pyscript-pwa.md`, optionally `platforms/index.md` matrix wording). Cross-link from Android TV / webOS / iOS docs-only notes so PWA is not reinvented per track.

**Not in this workstream:** new PWA runtime features or native shells — documentation and positioning only.

---

### iOS / iPadOS via PyScript

- Add a short note in `pydevices-examples` platform docs: Apple mobile = Mobile Safari + `PSDisplay` / PyScript gallery (browser and/or home-screen PWA — see PWA workstream above).
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

- Native iOS / iPadOS app (`pydevices-ios`, BeeWare/Kivy packaging, macOS CI for App Store)
- watchOS
- Nintendo Switch, PlayStation Vita, PS4/PS5 (org roadmap)
- Native webOS / Tizen Python or `SDLDisplay` on those OS shells (web path only — see pursue #3)

---

## Related

| Doc | Role |
|-----|------|
| [`AGENTS.md`](../AGENTS.md) | Cloud workspace layout |
| `pydevices-examples` platform docs | User-facing install/portability matrix |
