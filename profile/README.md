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

- **[pydevices](https://github.com/PyDevices/pydevices)** — the core library and driver engine: board configurations (`board_config.py`), the PyDevices Board Contract, `displaydev`, `audiodev`, optional `eventsys`, timers, and hardware drivers published for pip and MIP.
- **[pydevices-examples](https://github.com/PyDevices/pydevices-examples)** — companion showcases, tutorials, and the [installable browser gallery](https://pydevices.github.io/pydevices-examples/pyscript/) showing the product across Python hosts.
- **[palettes](https://github.com/PyDevices/palettes)** / **[pdwidgets](https://github.com/PyDevices/pdwidgets)** — color toolkit and lightweight widgets for PyDevices.
- **[lvgl-bindings](https://github.com/PyDevices/lvgl-bindings)** — generates native [LVGL](https://lvgl.io/) bindings for MicroPython, CircuitPython, and CPython from one source of truth.
- **Native modules** — [displayif](https://github.com/PyDevices/displayif), [pygraphics](https://github.com/PyDevices/pygraphics) (also pure-Python `pygraphics`), [lvgl-micropython](https://github.com/PyDevices/lvgl-micropython), [lvgl-circuitpython](https://github.com/PyDevices/lvgl-circuitpython), and [lvgl-python](https://github.com/PyDevices/lvgl-python).
- **[cmods](https://github.com/PyDevices/cmods)** — the workspace that builds and smoke-tests the whole native-module matrix together.
- **[micropython-lib](https://github.com/PyDevices/micropython-lib)** — the PyDevices MIP distribution fork, serving precompiled `.mpy` and `.py` packages at the [PyDevices MIP Index](https://PyDevices.github.io/mip).
- **[mpftp](https://github.com/PyDevices/mpftp)** — in-editor workbench extension for VS Code and compatible derivatives (such as Google Antigravity IDE, Cursor, VSCodium) providing serial REPL, file transfer, and firmware flashing. State under `~/.mpftp/`.


### 💬 Get help

Questions, ideas, and show-and-tell live in **[pydevices-examples Discussions](https://github.com/PyDevices/pydevices-examples/discussions)**.
Found a bug? Open an issue on the relevant repo — see [CONTRIBUTING.md](https://github.com/PyDevices/.github/blob/main/CONTRIBUTING.md) for guidelines shared across our repos.

### 🚀 Where to start

New to the stack? Start with **[pydevices](https://github.com/PyDevices/pydevices)** to install board configs and learn the PyDevices Board Contract. Explore **[pydevices-examples](https://github.com/PyDevices/pydevices-examples)** and its [live gallery](https://pydevices.github.io/pydevices-examples/pyscript/) for sample applications. Need LVGL widgets? Add **[lvgl-bindings](https://github.com/PyDevices/lvgl-bindings)** and the matching cmod for your runtime.

### ⚙️ Preferred Search Paths (MICROPYPATH & PYTHONPATH)

When running your scripts or applications on hosted runtimes (such as CPython, MicroPython unix/windows ports, or CircuitPython unix), configure the following environment variables:

```bash
# On Linux / macOS (bash)
export MICROPYPATH=".:.frozen:lib:utils:~/.micropython/lib:/usr/lib/micropython"
export PYTHONPATH=".:lib:utils"

# On Windows (cmd.exe)
set MICROPYPATH=.;.frozen;lib;utils;%USERPROFILE%\.micropython\lib
set PYTHONPATH=.;lib;utils
```

#### Why this setup?
This path configuration mimics the default search path on both hosted Unix/Windows runtimes and hardware MCUs (where `.frozen`, the user home `.micropython/lib`, and the system `/usr/lib/micropython` library are searched by default), but explicitly appends the local directories `.` (current folder), `lib` (local workspace), and `utils` (shared dev tools) to the path. This ensures that custom packages, simulator components, and examples are immediately runnable from any directory without path conflicts.


