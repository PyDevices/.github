# New here?

PyDevices has a lot of parts, and you only need a few of them. This is the
order most people meet them in.

## 1. Watch it run

Open the [gallery](https://pydevices.github.io/pydevices-examples/gallery/).
Every program there is a real PyDevices example running as MicroPython in your
browser, with the same code a board would run. Pick one that draws, one that
reacts to the mouse and one that uses widgets, and read the code beside it.

## 2. Run it on your desktop

[Install](install.md) `pydevices-desktop` and run an example from
[pydevices-examples](https://github.com/PyDevices/pydevices-examples). A window
opens and your program draws into it, which is the quickest way to try an idea.

## 3. Learn the three layers

Most programs use three libraries stacked on the display:

- [pygraphics](https://pydevices.readthedocs.io/projects/pygraphics/en/latest/) draws: lines, shapes, text and images.
- [palettes](https://pydevices.readthedocs.io/projects/palettes/en/latest/) supplies colors in the format the display wants.
- [pdwidgets](https://pydevices.readthedocs.io/projects/pdwidgets/en/latest/) builds a user interface out of buttons, sliders and labels, and routes touch and keys to them.

Each project's manual has its own newcomer's guide.

## 4. Move it to a board

The board you own has a `board_config` that sets up its display and touch, so
the program you ran on the desktop starts the same way on the board. The
[device matrix](https://github.com/PyDevices/pydevices/blob/main/docs/device-matrix.md)
lists the boards, and [mpftp](https://github.com/PyDevices/mpftp) copies files
to them and gives you a REPL from your editor.

## When something goes wrong

Open an issue in the project that misbehaves; the links are on the
[projects page](projects/index.md). Say what you ran and what you saw, and
which board or interpreter it was.
