# Docstring conventions

Public docstrings in the three library repositories — `palettes`, `pdwidgets`,
and `pygraphics` — are rendered on ReadTheDocs via mkdocstrings. Follow these
rules so the generated reference pages stay accurate. See
[building-docs.md](building-docs.md) for the build itself.

## Style

- **Google style** only (`Args`, `Returns`, `Raises`, `Example`).
- Do not mix Sphinx directives (`:return:`, `:param:`).
- Match **real function signatures** — do not document named parameters on `*args` / `**kwargs` wrappers.

## Module docstrings

One-line summary of the module's role. Optionally link to narrative docs:

```python
"""
displaydev display drivers.

See also: https://github.com/PyDevices/pydevices/blob/main/docs/displaydev.md
"""
```

## Class docstrings

- What the class is for and when to use it vs alternatives.
- `Args` for constructor parameters when non-obvious.
- Short usage example only when setup is not obvious (e.g. `App`, `BusDisplay`).

## Method / function docstrings

| Section | When required |
|---------|----------------|
| Summary line | Always |
| `Args` | Public methods with parameters |
| `Returns` | When return value matters (especially `Area` bounds) |
| `Raises` | When callers must handle errors |
| `Example` | Non-obvious usage only |

## Repository-specific notes

- **`Area` returns:** Drawing helpers that return dirty regions use `pygraphics.Area` (`x`, `y`, `w`, `h`).
- **App:** Document poll/subscribe patterns; link to [Events concept](https://github.com/PyDevices/pydevices/blob/main/docs/appdev.md).
- **Private API:** Names starting with `_` are excluded from mkdocstrings output; minimal or no docstrings are fine.
  Document public methods that live on private implementation bases when they surface via inheritance
  (e.g. provider `Timer` classes ← `_TimerCore.init` / `deinit` with `inherited_members: true`).

## Types

Type information goes in the **docstring**, not the signature. These packages
run on MicroPython, where annotations cost bytecode and RAM.

Stubs are the planned answer for pip consumers who want real types — see
[Planned: type stubs](publishing-automation.md#planned-type-stubs-for-every-published-package).
Do not add `py.typed` to a package: it tells a type checker to trust inline
annotations that deliberately are not there.

## Verification

From the repo root:

```bash
.venv-docs/bin/mkdocs build 2>&1 | grep -i griffe
```

Griffe warnings mean a docstring parameter does not appear in the signature — fix before merging P0 module changes.

## Priority tiers

| Tier | Modules |
|------|---------|
| P0 | `displaydev`, `appdev`, `events`, `keys`, `multimer` |
| P1 | `displaybuf`, `console`, other `utils` |
| P2 | Sibling packages document their own APIs: [pygraphics](https://pygraphics.readthedocs.io), [pdwidgets](https://pdwidgets.readthedocs.io), [palettes](https://palettes.readthedocs.io) |

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the PR workflow, and
[building-docs.md](building-docs.md) for how the generated API pages are built.
