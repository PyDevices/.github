# PyDevices Organization History

*Written 2026-09-06 from GitHub's repository records and the repositories' own histories; every creation date in the chronology was re-checked against GitHub the same day. Update the chronology when a repository is created, transferred, renamed or published.*

## Concise history

PyDevices began before the organization itself. The oldest project lineage starts on 2023-11-10 as Brad Barnett’s `mpdisplay` work: board configurations, display drivers, graphics, input events, and examples accumulated in one repository. CircuitPython support arrived in April 2024, followed by package extraction and broader desktop support.

On 2024-09-02 the code was rebranded “PyDevices”; GitHub records the organization’s creation the following day, 2024-09-03. On 2024-11-19 the original repository moved from `bdbarnett/mpdisplay` to `PyDevices/pydisplay`. Three supporting repositories followed: the imported LVGL MicroPython lineage, a `micropython-lib` fork, and `cmods`.

The organization assumed its current shape during June–August 2026. The large `pydisplay` repository was deliberately decomposed into display, LVGL, graphics, widget, palette, hardware, tooling, and examples repositories. An organization portal and shared publishing machinery were established in July; on 2026-08-11 the old flagship was refocused and renamed `pydevices-examples`, while the extracted hardware repository became the new `pydevices` flagship.

Late August and early September broadened the project substantially: Android and PyScript application paths, a browser/mobile Workbench, the CircuitPython-compatible audio stack, VST3 hosting, a versioned MicroPython overlay, native USB host/device support, and MIPI-CSI cameras. The audio component split shipped on 2026-09-03; `usbif` and `cameraif` were published on 2026-09-04.

The 2014 history in `mip`, the 2018 history in `lvgl-micropython`, and the 2024 history in `workbench` are inherited upstream histories—not evidence that PyDevices itself existed at those dates.

## Repository chronology

Dates are UTC calendar dates. “Created” is GitHub’s repository-object date, which survives transfers, forks, and renames.

| Repository | Created | Public / first verifiable public | Major milestones |
|---|---:|---:|---|
| [pydevices-examples](https://github.com/PyDevices/pydevices-examples) | 2023-11-10 | 2023-11-10* | Original monorepo; rebranded PyDevices 2024-09-02; transferred as `PyDevices/pydisplay` 2024-11-19; packages extracted through 2026; renamed/refocused as examples and PyScript gallery 2026-08-11. |
| [lvgl-micropython](https://github.com/PyDevices/lvgl-micropython) | 2024-11-17 | 2024-11-17* | Imported LVGL binding history reaching back to 2018; split into MicroPython-only glue in June 2026; adopted current name 2026-08-11. |
| [mip](https://github.com/PyDevices/mip) | 2024-11-22 | 2024-11-22* | Fork with inherited `micropython-lib` history from 2014; became PyDevices’ generated package mirror and MIP index; renamed from `micropython-lib` 2026-08-14. |
| [cmods](https://github.com/PyDevices/cmods) | 2024-12-03 | 2024-12-03* | Evolved into the optional build/integration workspace for MicroPython, CircuitPython, native modules, LVGL, USB, and JPEG support. |
| [displayif](https://github.com/PyDevices/displayif) | 2026-06-01 | ≤2026-06-25† | Native display-interface extraction, initially associated with `pydisplay_cmods`; standardized the DotClock/display API in July; added portable JPEG decoding in September. |
| [lvgl-bindings](https://github.com/PyDevices/lvgl-bindings) | 2026-06-18 | 2026-06-18* | Shared header-to-C generator; CPython target added 2026-06-19; automated LVGL 9.x release chain reached v9.5.22 by 2026-08-29. |
| [lvgl-circuitpython](https://github.com/PyDevices/lvgl-circuitpython) | 2026-06-18 | 2026-06-18* | CircuitPython LVGL integration and build glue; portable build and display-driver work; renamed from `lv_circuitpython_mod` 2026-08-11. |
| [lvgl-python](https://github.com/PyDevices/lvgl-python) | 2026-06-19 | 2026-06-19* | Native CPython extension, later covering Android and WebAssembly; first release 2026-06-30; reached v9.5.44 by 2026-08-29. |
| [pygraphics](https://github.com/PyDevices/pygraphics) | 2026-07-05 | 2026-07-05* | Unified native and pure-Python graphics across MP/CP/CPython; package renamed to `pygraphics` 2026-07-26; v0.0.38 on 2026-08-29. |
| [android-template](https://github.com/PyDevices/android-template) | 2026-07-06 | 2026-07-06* | Imported Android demo and python-for-android recipes from `usdl2`; produced the Launcher APK path; became the reusable application template. |
| [.github](https://github.com/PyDevices/.github) | 2026-07-12 | 2026-07-12* | Organization profile and community-health files; centralized releases in August; reusable publishing contract advanced from `publishing-v1` to `publishing-v9`. |
| [PyDevices.github.io](https://github.com/PyDevices/PyDevices.github.io) | 2026-07-12 | 2026-07-12* | Organization portal; consolidated project pages; introduced direct MicroPython WebAssembly/PyScript apps in August and the `pydevices.com` landing page in September. |
| [pdwidgets](https://github.com/PyDevices/pdwidgets) | 2026-07-14 | 2026-07-14* | Widget toolkit extracted from the monorepo; first release 2026-07-15; reached v0.0.23 on 2026-08-29. |
| [palettes](https://github.com/PyDevices/palettes) | 2026-07-15 | 2026-07-15* | Palette library extracted from `pydisplay` add-ons; first release immediately after extraction; v0.0.13 by 2026-08-29. |
| [mpftp](https://github.com/PyDevices/mpftp) | 2026-07-17 | 2026-07-17* | VS Code/Cursor MicroPython tooling for REPL, transfer, packages, and firmware; v0.0.1 on 2026-07-26 and v0.0.4 on 2026-08-29. |
| [pydevices](https://github.com/PyDevices/pydevices) | 2026-07-25 | 2026-07-25* | Began as the hardware/board-driver extraction from `pydisplay`; became the flagship portable package family in August; reached v0.3.8 on 2026-08-29. |
| [pyscript-template](https://github.com/PyDevices/pyscript-template) | 2026-08-12 | 2026-08-12* | Installable offline PWA template for browser-hosted PyDevices applications; repaired and standardized deployment contract on 2026-08-29. |
| [android-runner](https://github.com/PyDevices/android-runner) | 2026-08-17 | 2026-08-17* | Reproducible Android CPython runtime build engine; first Runner APK release, v0.1.0, on 2026-08-29. |
| [audioif](https://github.com/PyDevices/audioif) | 2026-08-25 | 2026-08-25* | CircuitPython audio APIs ported to MicroPython and CPython; cross-platform parity gates; v0.2.0 core-only split shipped with 21 wheels on 2026-09-03. |
| [workbench](https://github.com/PyDevices/workbench) | 2026-08-25 | 2026-08-25* | Public ViperIDE fork retaining history from 2024; rebranded with PyDevices WASM simulator and examples; v0.7.0 released 2026-08-29. |
| [workspace](https://github.com/PyDevices/workspace) | 2026-08-27 | Never; private | Private anchor for session bootstrap, maintainer tooling, program boards, and internal documentation; public builds do not depend on it. |
| [micropython-vst3](https://github.com/PyDevices/micropython-vst3) | 2026-08-27 | 2026-08-27* | Dedicated MicroPython VST3 instrument/effect engine; Windows and Linux byte-identical PCM, scripted synths, MIDI control, and REAPER validation. |
| [micropython-pydevices](https://github.com/PyDevices/micropython-pydevices) | 2026-08-29 | 2026-08-29* | Versioned MicroPython patch queue, runtime profiles, provenance, WebAssembly pieces, and restricted VST3-engine profile. |
| [usbif](https://github.com/PyDevices/usbif) | 2026-08-30 | 2026-09-04 | Developed privately, audited, and history-cleaned before publication; proved USB audio, MIDI, CDC, HID, storage, hub, UAC, and UVC paths in host/device roles. |
| [audiocomponents](https://github.com/PyDevices/audiocomponents) | 2026-09-01 | 2026-09-03 | Seeded from the audio work begun 2026-08-24; separated 53 instruments and effects from `audioif`; public v0.2.0 split shipped 2026-09-03. |
| [cameraif](https://github.com/PyDevices/cameraif) | 2026-09-04 | 2026-09-04 | Same-day bring-up and publication: board-agnostic camera API, MIPI-CSI capture, hardware JPEG, zero-copy frames, scaling, examples, and an upstream OV5647 report. |

\* Best-supported conclusion is that the repository was public from creation; GitHub exposes creation and current visibility but not a general historical “public since” field. I found no contrary visibility transition in the available history.

† `displayif` was definitely public under its earlier naming by 2026-06-25; the precise visibility-change instant between its 2026-06-01 creation and that public activity is unavailable. The organization audit-log endpoint that could settle this was inaccessible.

No files, branches, indexes, or repository configuration were changed while researching this history.
