<div align="center">

<img src="https://pydevices.github.io/assets/img/logo.svg" alt="PyDevices" width="64" height="64">

# PyDevices

**One display, input, and graphics stack. Three Python runtimes.**

[Website](https://pydevices.github.io/) · [Product](https://github.com/PyDevices/pydevices) · [Examples](https://github.com/PyDevices/pydevices-examples) · [Gallery](https://pydevices.github.io/pydevices-examples/pyscript/)

</div>

---

### What we build

PyDevices writes display, input, and graphics code once and runs it across
**MicroPython**, **CircuitPython**, and **CPython** — from microcontrollers to
the desktop and the browser.

- **[pydevices](https://github.com/PyDevices/pydevices)** — the reusable product source: `displaydev`, `audiodev`, optional `eventsys`, timers, board configs, and hardware drivers, published for pip and MIP.
- **[pydevices-examples](https://github.com/PyDevices/pydevices-examples)** — examples, tutorials, and the [installable browser gallery](https://pydevices.github.io/pydevices-examples/pyscript/) showing the product across MicroPython, CircuitPython, and CPython.
- **[palettes](https://github.com/PyDevices/palettes)** / **[pdwidgets](https://github.com/PyDevices/pdwidgets)** — color toolkit and lightweight widgets for PyDevices.
- **[lvgl-bindings](https://github.com/PyDevices/lvgl-bindings)** — generates native [LVGL](https://lvgl.io/) bindings for MicroPython, CircuitPython, and CPython from one source of truth.
- **Native modules** — [displayif](https://github.com/PyDevices/displayif), [pygraphics](https://github.com/PyDevices/pygraphics) (also pure-Python `pygraphics`), [lvgl-micropython](https://github.com/PyDevices/lvgl-micropython), [lvgl-circuitpython](https://github.com/PyDevices/lvgl-circuitpython), and [lvgl-python](https://github.com/PyDevices/lvgl-python).
- **[cmods](https://github.com/PyDevices/cmods)** — the workspace that builds and smoke-tests the whole native-module matrix together.
- **App templates** — [pydevices-android-template](https://github.com/PyDevices/pydevices-android-template) for native Android APKs and [pydevices-pyscript-template](https://github.com/PyDevices/pydevices-pyscript-template) for installable browser PWAs.
- **[mpftp](https://github.com/PyDevices/mpftp)** — VS Code / Cursor board tools (REPL, file transfer, firmware). State under `~/.mpftp/`.

### 💬 Get help

Questions, ideas, and show-and-tell live in **[pydevices-examples Discussions](https://github.com/PyDevices/pydevices-examples/discussions)**.
Found a bug? Open an issue on the relevant repo — see [CONTRIBUTING.md](https://github.com/PyDevices/.github/blob/main/CONTRIBUTING.md) for guidelines shared across our repos.

### 🚀 Where to start

New to the stack? Browse **[pydevices-examples](https://github.com/PyDevices/pydevices-examples)** and its [live gallery](https://pydevices.github.io/pydevices-examples/pyscript/), then install packages or a board config from **[pydevices](https://github.com/PyDevices/pydevices)**. Need LVGL widgets? Add **[lvgl-bindings](https://github.com/PyDevices/lvgl-bindings)** and the matching cmod for your runtime.
