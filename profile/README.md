<div align="center">

<img src="https://pydevices.github.io/assets/img/logo.svg" alt="PyDevices" width="64" height="64">

# PyDevices

**One display, input, and graphics stack. Three Python runtimes.**

[Website](https://pydevices.github.io/) · [pydisplay](https://github.com/PyDevices/pydisplay) · [Docs](https://pydisplay.readthedocs.io) · [lvgl-bindings](https://github.com/PyDevices/lvgl-bindings)

</div>

---

### What we build

PyDevices writes display, input, and graphics code once and runs it across
**MicroPython**, **CircuitPython**, and **CPython** — from microcontrollers to
the desktop and the browser.

- **[pydisplay](https://github.com/PyDevices/pydisplay)** — pure-Python display, input, and event drivers. The foundation of the stack. Try it live in the [browser demos](https://pydevices.github.io/pydisplay/pyscript/) or read the [docs](https://pydisplay.readthedocs.io).
- **[palettes](https://github.com/PyDevices/palettes)** / **[pdwidgets](https://github.com/PyDevices/pdwidgets)** — color toolkit and lightweight widgets for pydisplay.
- **[micropython-hardware](https://github.com/PyDevices/micropython-hardware)** — board configs and hardware drivers for MicroPython and CircuitPython.
- **[lvgl-bindings](https://github.com/PyDevices/lvgl-bindings)** — generates native [LVGL](https://lvgl.io/) bindings for MicroPython, CircuitPython, and CPython from one source of truth.
- **Native modules** — [displayif](https://github.com/PyDevices/displayif), [pygraphics](https://github.com/PyDevices/pygraphics) (also pure-Python `pygraphics`), [lvgl-micropython](https://github.com/PyDevices/lvgl-micropython), [lvgl-circuitpython](https://github.com/PyDevices/lvgl-circuitpython), and [lvgl-python](https://github.com/PyDevices/lvgl-python).
- **[cmods](https://github.com/PyDevices/cmods)** — the workspace that builds and smoke-tests the whole native-module matrix together.
- **[pydisplay_android](https://github.com/PyDevices/pydisplay_android)** — the Android APK path for pydisplay.
- **[mpftp](https://github.com/PyDevices/mpftp)** — VS Code / Cursor board tools (REPL, file transfer, firmware). State under `~/.mpftp/`.

### 💬 Get help

Questions, ideas, and show-and-tell live in **[pydisplay Discussions](https://github.com/PyDevices/pydisplay/discussions)**.
Found a bug? Open an issue on the relevant repo — see [CONTRIBUTING.md](https://github.com/PyDevices/.github/blob/main/CONTRIBUTING.md) for guidelines shared across our repos.

### 🚀 Where to start

New to the stack? Start with **[pydisplay](https://github.com/PyDevices/pydisplay)** and its [documentation](https://pydisplay.readthedocs.io). Need LVGL widgets? Add **[lvgl-bindings](https://github.com/PyDevices/lvgl-bindings)** and the matching cmod for your runtime.
