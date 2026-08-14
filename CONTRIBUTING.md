# 🤝 Contributing to PyDevices

Thanks for your interest in contributing! PyDevices spans several repos —
this doc covers what's shared across all of them. Each repo's own `README.md`
(and `AGENTS.md`, where present) has project-specific setup, test, and lint
instructions — read that first.

## Where things live

Repo directory and root-file layout (`src/`, `lib/`, `tests/`,
`requirements-dev.txt`, …): see [`docs/repo-layout.md`](docs/repo-layout.md).

- **[pydevices](https://github.com/PyDevices/pydevices)** — core display, touch, and hardware abstraction layer (HAL) library.
- **[pydevices-examples](https://github.com/PyDevices/pydevices-examples)** — showcase apps, PyScript runner, and reference gallery.
- **[palettes](https://github.com/PyDevices/palettes)** / **[pdwidgets](https://github.com/PyDevices/pdwidgets)** — color engine and lightweight UI widgets.
- **[mpftp](https://github.com/PyDevices/mpftp)** — VS Code / Cursor board tools (REPL, file transfer, firmware).
- **[lvgl-bindings](https://github.com/PyDevices/lvgl-bindings)** — the LVGL binding generator; source of truth for the native LVGL cmods.
- **Native modules** — [displayif](https://github.com/PyDevices/displayif), [pygraphics](https://github.com/PyDevices/pygraphics) (also pure-Python `pygraphics`), [lvgl-micropython](https://github.com/PyDevices/lvgl-micropython), [lvgl-circuitpython](https://github.com/PyDevices/lvgl-circuitpython), [lvgl-python](https://github.com/PyDevices/lvgl-python).
- **[cmods](https://github.com/PyDevices/cmods)** — workspace wrapper that builds/smoke-tests the native cmods together.
- **[pydevices-android-template](https://github.com/PyDevices/pydevices-android-template)** — Android packaging (python-for-android/buildozer).
- **[pydevices-pyscript-template](https://github.com/PyDevices/pydevices-pyscript-template)** — installable PyScript/PWA application starter.

If you're not sure which repo an issue or PR belongs to, open it on
[pydevices-examples](https://github.com/PyDevices/pydevices-examples/issues) — we'll help route it.

## 🐛 Reporting bugs / requesting features

Use the issue templates on the relevant repo. Include the runtime
(MicroPython/CircuitPython/CPython), version, and platform/board where
applicable — most bugs here are runtime- or hardware-specific.

For open-ended questions, ideas, or show-and-tell, use
[pydevices-examples Discussions](https://github.com/PyDevices/pydevices-examples/discussions)
instead of opening an issue.

## Pull requests

1. Fork the repo and branch from `main`.
2. Follow that repo's existing code style and test conventions (see its
   `README.md` / `AGENTS.md`).
3. Keep PRs focused — one change per PR is easier to review and revert.
4. Describe *why* the change is needed, not just what changed.

## Regenerating LVGL bindings

If your change touches `lvgl-bindings/binding/`, `lv_conf.h`, or the `lvgl`
submodule, regenerate and commit the affected `generated/*.c` files — see
[lvgl-bindings' README](https://github.com/PyDevices/lvgl-bindings#generate-bindings)
for the exact commands. Don't hand-edit generated files.

## Doc style: emoji

Docs across PyDevices use a small, fixed set of emoji as landmarks on
section headings — not decoration. Each emoji has exactly one meaning and is
only used on a heading that's actually about that thing:

| Emoji | Meaning | Use on headings like |
|---|---|---|
| 🚀 | Getting started / install / build | "Quick start", "Installation", "Build", "Setup" |
| 🎨 | Examples / demos | "Examples", "App starter", a demo's own title |
| 💬 | Getting help / support | "Get help", "Getting help", "Still stuck?" |
| 🐛 | Reporting bugs / issues | "Reporting bugs", "Reporting bugs / requesting features" |
| 🤝 | Contributing | "Contributing" (as a heading or doc title) |
| 📚 | Documentation / reference links | "Documentation map", "Quick links" |
| ⚠️ | Troubleshooting / things that can go wrong | "Troubleshooting" (doc title), a warning callout |

Rules of thumb:

- Only use these seven — don't add a new one-off emoji to "break up the
  monotony." If a heading doesn't match one of these meanings, leave it
  plain.
- One emoji per heading, and only on headings, not scattered through body
  text (an inline `⚠️ **Note:**` callout is the one exception).
- Skip a doc/repo entirely if it doesn't have a heading that genuinely
  matches — don't invent a "Getting started" section just to have somewhere
  to put 🚀.
- If several headings in the same doc are parallel alternatives for the
  same category (e.g. "Build (Make ports)" *and* "Build (CMake ports)"),
  tag none of them rather than picking one arbitrarily — repeating the same
  emoji on adjacent headings reads as noise, not a landmark.
