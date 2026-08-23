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
| **Docs only** | PWA (Simulator & template — **where they run**); iOS / iPadOS via PyScript |
| **Not a platform track** | FreeRTOS board expansion; Zephyr |
| **Ruled out** | Native iOS; watchOS; Switch / Vita / PS; native webOS / Tizen |

## Decisions (per target, 2026-07-15 triage)

| Target | Feasibility | Org decision | Notes |
|--------|:-----------:|--------------|-------|
| Linux fbdev / DRM / KMS (no WM) | Medium–High | **Pursue** | SDL `kmsdrm` first; native fbdev/DRM only if needed. Parallel with other pursue tracks. Why-comments on KMS edits. |
| Android TV / Fire OS | Medium–High | **Pursue** | Phone Android treated as stable. Why-comments on new edits. |
| LG webOS / Samsung Tizen (web) | Low–Medium | **Pursue** (web only) | PyScript TV examples + remote/key bridge; **no native SDL**. Why-comments on new edits. |
| iOS / iPadOS via PyScript | Low–Medium | **Docs note only** | Position Mobile Safari / `PSDisplay` in platform docs; no dedicated smoke campaign. |
| Progressive Web Apps (PyScript) | N/A (ships today) | **Docs only** | Centralized in PyDevices Simulator & `pyscript-template` — document **where PWAs run** (browser×OS×install UX) in platform docs. |
| Native iOS / iPadOS app | Low–Medium | **Ruled out** | Foreseeable roadmap: Apple path is PyScript-in-Safari (docs note) only. |
| Apple watchOS | Very Low | **Ruled out** | Entirely. |
| FreeRTOS / new MCU boards | Medium (via MP) | **Not a platform track** | Normal `displayif` + board_config product work. |
| Zephyr RTOS | Low–Medium | **Not a platform track** | Only if a specific board need appears later. |
| Nintendo Switch / Vita / PS | Very Low | **Ruled out** | Org roadmap — no consoles. |

**Parallel OK:** Linux KMS, Android TV, and webOS/Tizen web may proceed independently (no forced sequence).

---

## Pursue workstreams

### Linux KMS (no window manager)

- Primary test path: standard CPython venv on desktop Linux with `SDL_VIDEODRIVER=kmsdrm` (VT console or headless VM).
- Validate displaydev / SDL2 initialization and frame loop under KMS.
- Include why-comments on any KMS-specific workarounds.

---

### Android TV / Fire OS

- Validate remote D-pad navigation and key event mapping (`keys.K_UP`, `keys.K_DOWN`, `keys.K_SELECT`).
- Ensure landscape orientation lock and overscan margins for TV displays.

---

### LG webOS / Samsung Tizen (web only)

- TV browsers run Chromium; leverage PyScript web stack.
- Remote control input mapped to keyboard chords.

---

## Docs only

### Progressive Web Apps (PWA)

**Goal:** Treat installable / offline PyScript apps as a **first-class** platform story, documented as clearly as MCU / desktop / Android APK — especially **where** a PyDevices PWA actually runs.

The how-to lives with the repo that owns the subject: [`pyscript-template/docs/pwa-guide.md`](https://github.com/PyDevices/pyscript-template/blob/main/docs/pwa-guide.md) (manifest, service worker, COI, GitHub Pages), alongside the centralized offline [PyDevices Simulator](https://pydevices.github.io/simulator/).

**Remaining:**

- The host matrix in that guide should stay current; it covers at least:
  - Desktop Chromium (Chrome / Edge) — install prompt / standalone window
  - Android Chrome — install / home-screen; contrast with native `android-template` APK
  - iOS / iPadOS Safari — Share → Add to Home Screen (no `beforeinstallprompt`)
  - Chromebook and other desktop Linux browsers as relevant
  - Relation to TV **web** path (webOS / Tizen Chromium browsers — browser or installable web app, not native SDL)
- Clarify standalone vs tab behavior, offline/cache expectations, and install UX differences per host.
- Keep implementation detail in the PWA how-to; **platform docs own “where it runs.”**

**Touchpoints:** `pyscript-template` (`docs/pwa-guide.md`) and `PyDevices.github.io` (`simulator/`). Cross-link from Android TV / webOS / iOS docs-only notes so PWA is not reinvented per track.

**Not in this workstream:** new PWA interpreter features or native shells — documentation and positioning only.

### iOS / iPadOS via PyScript

- Apple mobile is supported via Mobile Safari + `PSDisplay` / PyScript (browser and/or home-screen PWA).
- Does not reopen native iOS packaging.

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
