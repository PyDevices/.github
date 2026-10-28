# Install

How you install PyDevices depends on where your code will run. The exact
commands and the system packages each channel needs are in the
[install workflows](https://github.com/PyDevices/pydevices/blob/main/docs/install-workflows.md)
of the `pydevices` repository; this page is the short version.

::::{tab-set}

:::{tab-item} MicroPython board
Install a package with `mip`, pointing it at the PyDevices index:

```python
import mip
mip.install("palettes", index="https://PyDevices.github.io/mip")
```

A board's `board_config` installs the same way and wires up the display and
touch for that board. The board's page in the
[device matrix](https://github.com/PyDevices/pydevices/blob/main/docs/device-matrix.md)
names the package to ask for.
:::

:::{tab-item} CircuitPython board
Copy the library's folder from its repository into `CIRCUITPY/lib/`. Libraries
that have a C part (pygraphics) are built into a CircuitPython firmware
instead; each project's page says which.
:::

:::{tab-item} Desktop Python
One command installs the whole desktop stack:

```bash
pip install -i https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ pydevices-desktop
```

Current releases are on TestPyPI, which is why the command names it first.
:::

:::{tab-item} In the browser
Nothing to install: the [gallery](https://pydevices.github.io/gallery/gallery/)
and [Workbench](https://pydevices.github.io/workbench/) run MicroPython as
WebAssembly. To use a library from your own page, load it with micropip in
Pyodide or PyScript; each project's page shows the line.
:::

::::

## Checking that it works

With `pydevices-desktop` installed, this draws a red square in a window:

```bash
python -c "from board_config import display_drv; display_drv.fill_rect(50, 50, 100, 100, 0xF800); display_drv.show()"
```

If a window opens with a red square in it, the stack is working. If it does
not, the
[troubleshooting page](https://github.com/PyDevices/pydevices/blob/main/docs/troubleshooting.md)
is the next stop.
