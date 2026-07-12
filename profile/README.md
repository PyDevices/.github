<div align="center">

<img src="https://pydevices.github.io/assets/img/logo.svg" alt="PyDevices" width="64" height="64">

# PyDevices

**One display, input, and graphics stack. Three Python runtimes.**

[Website](https://pydevices.github.io/) · [pydisplay](https://github.com/PyDevices/pydisplay) · [Docs](https://pydisplay.readthedocs.io) · [lv_bindings](https://github.com/PyDevices/lv_bindings)

</div>

---

### What we build

PyDevices writes display, input, and graphics code once and runs it across
**MicroPython**, **CircuitPython**, and **CPython** — from microcontrollers to
the desktop and the browser.

- **[pydisplay](https://github.com/PyDevices/pydisplay)** — pure-Python display, input, and event drivers. The foundation of the stack. Try it live in the [browser demos](https://pydevices.github.io/pydisplay/pyscript/) or read the [docs](https://pydisplay.readthedocs.io).
- **[lv_bindings](https://github.com/PyDevices/lv_bindings)** — generates native [LVGL](https://lvgl.io/) bindings for MicroPython, CircuitPython, and CPython from one source of truth.
- **Native cmods** — [displayif](https://github.com/PyDevices/displayif), [graphics](https://github.com/PyDevices/graphics), [usdl2](https://github.com/PyDevices/usdl2), [lv_micropython_cmod](https://github.com/PyDevices/lv_micropython_cmod), [lv_circuitpython_mod](https://github.com/PyDevices/lv_circuitpython_mod), and [lv_cpython_mod](https://github.com/PyDevices/lv_cpython_mod) — the C modules that give pydisplay real hardware speed and an LVGL widget toolkit.
- **[cmods](https://github.com/PyDevices/cmods)** — the workspace that builds and smoke-tests the whole native-module matrix together.
- **[pydisplay_android](https://github.com/PyDevices/pydisplay_android)** — the Android APK path for pydisplay.

### 💬 Get help

Questions, ideas, and show-and-tell live in **[pydisplay Discussions](https://github.com/PyDevices/pydisplay/discussions)**.
Found a bug? Open an issue on the relevant repo — see [CONTRIBUTING.md](https://github.com/PyDevices/.github/blob/main/CONTRIBUTING.md) for guidelines shared across our repos.

### 🚀 Where to start

New to the stack? Start with **[pydisplay](https://github.com/PyDevices/pydisplay)** and its [documentation](https://pydisplay.readthedocs.io). Need LVGL widgets? Add **[lv_bindings](https://github.com/PyDevices/lv_bindings)** and the matching cmod for your runtime.
