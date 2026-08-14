# PyDevices Organization Architecture & Functional Tiering

This document outlines the functional architecture, repository organization, and environment search paths across the **PyDevices** organization.

---

## 1. Functional Tiering Overview

The 17 repositories in the PyDevices organization are structured into clear functional tiers:

```
                               ┌────────────────────────────────────────────────────────┐
                               │                 PyDevices Core Engine                  │
                               │                       `pydevices`                      │
                               │    (Board Contract, displaydev, audiodev, multimer)    │
                               └───────────────────────────┬────────────────────────────┘
                                                           │
                                           ┌───────────────┴───────────────┐
                                           │ Native Display C Modules      │
                                           │          `displayif`          │
                                           └───────────────┬───────────────┘
                                                           │
        ┌───────────────────┬───────────────────────────────┼───────────────────────────────┬───────────────────┐
        ▼                   ▼                               ▼                               ▼                   ▼
┌───────────────┐   ┌───────────────┐               ┌───────────────┐               ┌───────────────┐   ┌───────────────┐
│ Packaging Hub │   │ Pure-Python   │               │ LVGL C-Native │               │ Developer     │   │ Showcase &    │
│ `micropython- │   │ Toolkits      │               │ Stack         │               │ Workbench     │   │ Templates     │
│     lib`      │   │ `pygraphics`  │               │ `lvgl-        │               │   `mpftp`     │   │ `pydevices-   │
│  (MIP Index)  │   │  `palettes`   │               │  bindings`    │               │   `cmods`     │   │  examples`    │
└───────────────┘   │ `pdwidgets`   │               │ `lvgl-*`      │               └───────────────┘   │ `pydevices-   │
                    └───────────────┘               └───────────────┘                                   │  *-template`  │
                                                                                                        └───────────────┘
```

---

## 2. Functional Tier Breakdown

### Tier 1: Core Engine & Native Display C Modules
* **[`pydevices`](https://github.com/PyDevices/pydevices)**: Core framework owning hardware board configurations (`board_config.py`), the PyDevices Board Contract, `displaydev`, `audiodev`, `multimer`, `eventsys`, and core hardware drivers.
* **[`displayif`](https://github.com/PyDevices/displayif)**: Low-level native C display interface bus modules (SPI, I80 parallel, RGB dotclock, MIPI DSI, PicoDVI, USDL2) consumed by `pydevices` display backends.

### Tier 2: Pure-Python & Portable Toolkits (Zero External Dependencies)
* **[`pygraphics`](https://github.com/PyDevices/pygraphics)**: Standalone 2D graphics engine providing expanded `FrameBuffer` primitives, dirty `Area` returns, 24-bit True Color (`RGB888`), custom font engines, and image I/O. (Includes optional C acceleration fallback).
* **[`palettes`](https://github.com/PyDevices/palettes)**: Zero-dependency color palette toolkit providing pre-computed HSV color wheels, Material Design palettes, RGB color cubes, and indexed system colors.
* **[`pdwidgets`](https://github.com/PyDevices/pdwidgets)**: Pure-Python UI widget toolkit (`Button`, `Label`, `Screen`, `List`) built on `pygraphics` and `palettes`, requiring zero C compilation.

### Tier 3: Packaging & Index Infrastructure
* **[`micropython-lib`](https://github.com/PyDevices/micropython-lib)**: PyDevices distribution index serving precompiled `.mpy` bytecode and `.py` source packages via MIP at `https://PyDevices.github.io/mip`.

### Tier 4: LVGL Native C Stack
* **[`lvgl-bindings`](https://github.com/PyDevices/lvgl-bindings)**: Core binding generator and shared `display_driver.py` coordinator.
* **[`lvgl-micropython`](https://github.com/PyDevices/lvgl-micropython)**: MicroPython user C module integration for LVGL.
* **[`lvgl-python`](https://github.com/PyDevices/lvgl-python)**: CPython extension published as `pydevices-lvgl` wheels on TestPyPI.
* **[`lvgl-circuitpython`](https://github.com/PyDevices/lvgl-circuitpython)**: Out-of-tree patch set for CircuitPython LVGL integration.

### Tier 5: Developer Workbench & Tooling
* **[`mpftp`](https://github.com/PyDevices/mpftp)**: In-editor workbench extension for VS Code and compatible derivatives (Google Antigravity IDE, Cursor, VSCodium) featuring serial REPL in the Terminal panel, dual-pane FTP file transfer, and firmware flashing.
* **[`cmods`](https://github.com/PyDevices/cmods)**: Optional aggregation build workspace (`build_mp.sh`, `build_cp.sh`, `build_runtimes.sh`) for building multi-module MicroPython and CircuitPython firmware.

### Tier 6: Showcase Gallery & Application Starter Templates
* **[`pydevices-examples`](https://github.com/PyDevices/pydevices-examples)**: Showcase gallery, application examples, and cross-runtime test harnesses.
* **[`pydevices-android-template`](https://github.com/PyDevices/pydevices-android-template)**: Buildozer starter template for building Android APKs with Python-for-Android and SDL2.
* **[`pydevices-pyscript-template`](https://github.com/PyDevices/pydevices-pyscript-template)**: Starter template for standalone installable PyScript PWA web applications.

---

## 3. Preferred Search Paths (`MICROPYPATH` & `PYTHONPATH`)

When running scripts or applications on hosted runtimes (such as CPython, MicroPython unix/windows ports, or CircuitPython unix), configure the following environment variables:

```bash
# On Linux / macOS (bash)
export MICROPYPATH=".:.frozen:lib:utils:~/.micropython/lib:/usr/lib/micropython"
export PYTHONPATH=".:lib:utils"

# On Windows (cmd.exe)
set MICROPYPATH=.;.frozen;lib;utils;%USERPROFILE%\.micropython\lib
set PYTHONPATH=.;lib;utils
```

### Rationale
This path configuration mirrors the default search path on both hosted Unix/Windows runtimes and hardware MCUs (where `.frozen`, the user home `.micropython/lib`, and the system `/usr/lib/micropython` library are searched by default), while explicitly appending `.` (current folder), `lib` (local workspace), and `utils` (shared dev tools). This ensures custom packages and examples remain runnable without path conflicts.

---

## 4. Non-Intrusive Workflow Guarantee

All workflow helpers (`cmods`, `mpftp`, `micropython-lib` custom MIP index) are **100% optional**. Experienced developers retain complete freedom to use traditional `make USER_C_MODULES=...`, stock `mpremote`, `circup`, or standalone IDEs without modifying their habits.
