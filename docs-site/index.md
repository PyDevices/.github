# PyDevices

```{raw} html
<div class="hero-banner">
  <p><strong>One Python for screens, sound and USB</strong> that runs the same on a microcontroller, on your desktop and in a browser tab.</p>
  <div class="badge-row">
    <span class="badge badge-brand">MicroPython</span>
    <span class="badge badge-brand">CircuitPython</span>
    <span class="badge badge-brand">CPython</span>
    <span class="badge badge-brand">WebAssembly</span>
    <span class="badge">Alpha</span>
  </div>
</div>
```

PyDevices is a set of libraries and firmware for people who build things with
displays, touch, sound and USB in Python. You write your drawing, widgets and
audio code once and run it on a microcontroller board, as a desktop program,
inside a web page, or on Android.

This site is the front door to the documentation of every PyDevices project.
Each project has its own manual, and the bar at the top of every page takes
you to any of them. If you are new, start with the
[newcomer's guide](newcomers.md); if you want something on your machine,
[install](install.md) it.

## The projects

::::{grid} 1 1 2 3
:gutter: 3

:::{grid-item-card} palettes
:link: https://palettes.readthedocs.io/
:link-type: url
Color palettes: an HSV wheel, RGB cubes, Material Design swatches and RGB565
helpers.
:::

:::{grid-item-card} pygraphics
:link: https://pygraphics.readthedocs.io/
:link-type: url
2D drawing, bitmap fonts and blitting, in C and in Python.
:::

:::{grid-item-card} pdwidgets
:link: https://pdwidgets.readthedocs.io/
:link-type: url
Buttons, sliders, labels and screens for touch displays, in pure Python.
:::
::::

Every project, including the ones whose manual is still a README on GitHub, is
listed in [Projects](projects/index.md).

## Try it before you install it

The [gallery](https://pydevices.github.io/pydevices-examples/gallery/) runs
the same example programs that run on boards, in your browser, and
[Workbench](https://pydevices.github.io/workbench/) is an editor with a
simulated board built in. The main page of each project here also carries a
live demo you can edit and run.

```{toctree}
:hidden:
:maxdepth: 2

newcomers
install
projects/index
```
