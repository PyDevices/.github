# New here?

OmniPython has a lot of parts, and you only need a few of them. This is the
order most people meet them in.

## 1. Watch it run

Open the [gallery](https://gallery.omnipython.org/).
Every program there is a real OmniPython example running as MicroPython in your
browser, with the same code a board would run. Pick one that draws, one that
reacts to the mouse and one that uses widgets, and read the code beside it.

## 2. Run it on your desktop

[Install](install.md) `omnipython-desktop` and run an example from
[gallery](https://github.com/PyDevices/gallery). A window
opens and your program draws into it, which is the quickest way to try an idea.

## 3. Learn the three layers

Most programs use these libraries stacked on the display:

- [pygraphics](pygraphics/index.md) draws: lines, shapes, text and images.
- [palettes](palettes/index.md) supplies colors in the format the display wants.
- [LVGL](lvgl/index.md) is the toolkit to reach for when you want buttons, sliders and labels, with touch and keys routed to them.

[pdwidgets](pdwidgets/index.md) is a different kind of library: a whole widget
toolkit written in Python on the OmniPython core, with no C. It's there to show
that the core can carry a UI framework, and it isn't part of release firmware.

Each library's section starts with its own install page and first program.

## 4. Move it to a board

The board you own has a `board_config` that sets up its display and touch, so
the program you ran on the desktop starts the same way on the board. The
[board list](omnipython/boards/board-configs.md)
lists the boards, and [mcuctl](https://github.com/PyDevices/mcuctl) copies files
to them and gives you a REPL from your editor.

## When something goes wrong

Open an issue in the repository of the library that misbehaves; the
"Edit on GitHub" link at the top of its pages leads there. Say what you ran and what you saw, and
which board or interpreter it was.
