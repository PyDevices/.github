# Install

How you install OmniPython depends on where your code will run. The exact
commands and the system packages each channel needs are in the
[omnipython install guide](omnipython/get-started/install.md); this page is the
short version.

::::{tab-set}

:::{tab-item} MicroPython board
Install a package with `omip`, which looks on the OmniPython index and brings
what the package needs:

```python
import omip
omip.install("palettes")
```

`omip` comes with OmniPython firmware. On other MicroPython firmware, run
`mip.install("github:PyDevices/omnipython/lib/omip.py")` once to put it on the board.

A board's `board_config` installs the same way and wires up the display and
touch for that board. The board's row in the
[board list](omnipython/boards/board-configs.md)
names the package to ask for.
:::

:::{tab-item} CircuitPython board
Copy the library's folder from its repository into `CIRCUITPY/lib/`. Libraries
that have a C part (pygraphics) are built into a CircuitPython firmware
instead; each library's install page says which.
:::

:::{tab-item} Desktop Python
One command installs the whole desktop stack:

```bash
pip install --pre omnipython-desktop
```

Current releases are pre-releases, which is why the command asks for them with `--pre`.
:::

:::{tab-item} In the browser
Nothing to install: the [gallery](https://gallery.omnipython.org/)
and [Workbench](https://workbench.pydevices.com/) run MicroPython as
WebAssembly. To use a library from your own page, load it with micropip in
Pyodide or PyScript; each library's install page shows the line.
:::

::::

## Checking that it works

With `omnipython-desktop` installed, this draws a red square in a window:

```bash
python -c "from board_config import display_drv; display_drv.fill_rect(50, 50, 100, 100, 0xF800); display_drv.show()"
```

If a window opens with a red square in it, the stack is working. If it does
not, the
[troubleshooting page](omnipython/guides/troubleshooting.md)
is the next stop.
