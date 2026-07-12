# Contributing to PyDevices

Thanks for your interest in contributing! PyDevices spans several repos —
this doc covers what's shared across all of them. Each repo's own `README.md`
(and `AGENTS.md`, where present) has project-specific setup, test, and lint
instructions — read that first.

## Where things live

- **[pydisplay](https://github.com/PyDevices/pydisplay)** — the core display/input/graphics library (pure Python).
- **[lv_bindings](https://github.com/PyDevices/lv_bindings)** — the LVGL binding generator; source of truth for the native LVGL cmods.
- **Native cmods** — [displayif](https://github.com/PyDevices/displayif), [graphics](https://github.com/PyDevices/graphics), [usdl2](https://github.com/PyDevices/usdl2), [lv_micropython_cmod](https://github.com/PyDevices/lv_micropython_cmod), [lv_circuitpython_mod](https://github.com/PyDevices/lv_circuitpython_mod), [lv_cpython_mod](https://github.com/PyDevices/lv_cpython_mod).
- **[cmods](https://github.com/PyDevices/cmods)** — workspace wrapper that builds/smoke-tests the native cmods together.
- **[pydisplay_android](https://github.com/PyDevices/pydisplay_android)** — Android packaging (python-for-android/buildozer).

If you're not sure which repo an issue or PR belongs to, open it on
[pydisplay](https://github.com/PyDevices/pydisplay/issues) — we'll help route it.

## Reporting bugs / requesting features

Use the issue templates on the relevant repo. Include the runtime
(MicroPython/CircuitPython/CPython), version, and platform/board where
applicable — most bugs here are runtime- or hardware-specific.

For open-ended questions, ideas, or show-and-tell, use
[pydisplay Discussions](https://github.com/PyDevices/pydisplay/discussions)
instead of opening an issue.

## Pull requests

1. Fork the repo and branch from `main`.
2. Follow that repo's existing code style and test conventions (see its
   `README.md` / `AGENTS.md`).
3. Keep PRs focused — one change per PR is easier to review and revert.
4. Describe *why* the change is needed, not just what changed.

## Regenerating LVGL bindings

If your change touches `lv_bindings/binding/`, `lv_conf.h`, or the `lvgl`
submodule, regenerate and commit the affected `generated/*.c` files — see
[lv_bindings' README](https://github.com/PyDevices/lv_bindings#generate-bindings)
for the exact commands. Don't hand-edit generated files.
