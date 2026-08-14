# PyDevices Ecosystem

Welcome to **PyDevices** — a unified pure-Python hardware abstraction engine, 2D graphics toolkit, native LVGL C binding generator, and cross-platform app host across MicroPython, CircuitPython, CPython, PyScript, and Android.

---

## 🏛️ Ecosystem Structure

- **Org Landing Portal**: [PyDevices.github.io](https://pydevices.github.io/)
- **MIP Package Index**: [PyDevices MIP Index](https://pydevices.github.io/mip/)
- **Centralized Assets & Scripts**: [.github (*dotgithub*)](https://github.com/PyDevices/.github)

---

## ⚡ 5-Tier Repository Overview

1. **Tier 1: Core Platform & Board Contract**
   - [`pydevices`](https://github.com/PyDevices/pydevices): Standardized hardware abstraction layer.
   - [`displayif`](https://github.com/PyDevices/displayif): C bus usermod engine.
   - [`pydevices-examples`](https://github.com/PyDevices/pydevices-examples): Showcase apps and live PyScript sandbox.

2. **Tier 2: Pure-Python & Portable Toolkits**
   - [`pygraphics`](https://github.com/PyDevices/pygraphics): 0-dependency 2D FrameBuffer engine.
   - [`pdwidgets`](https://github.com/PyDevices/pdwidgets): Pure-Python widget toolkit.
   - [`palettes`](https://github.com/PyDevices/palettes): High-performance color space & palette converter.

3. **Tier 3: LVGL Native Extensions & Binding Generator**
   - [`lvgl-bindings`](https://github.com/PyDevices/lvgl-bindings): Single-source LVGL C header parser & binding generator.
   - [`lvgl-micropython`](https://github.com/PyDevices/lvgl-micropython): MicroPython C usermod.
   - [`lvgl-python`](https://github.com/PyDevices/lvgl-python): CPython / Pyodide WASM bindings.
   - [`lvgl-circuitpython`](https://github.com/PyDevices/lvgl-circuitpython): CircuitPython C usermod.

4. **Tier 4: Target App Hosts & PWA Templates**
   - [`pydevices-pyscript-template`](https://github.com/PyDevices/pydevices-pyscript-template): Progressive Web App (PWA) template.
   - [`pydevices-android-template`](https://github.com/PyDevices/pydevices-android-template): Android APK host template.

5. **Tier 5: Developer Tools & Infrastructure**
   - [`mip`](https://github.com/PyDevices/mip): MIP package index.
   - [`cmods`](https://github.com/PyDevices/cmods): Multi-usermod C build workspace.
   - [`mpftp`](https://github.com/PyDevices/mpftp): Serial & FTP REPL transfer workbench.
