# Docstring conventions

Public docstrings in the three library projects — `palettes`, `pdwidgets`,
and `pygraphics` — are rendered on Read the Docs by Sphinx's `autodoc` with the
`napoleon` extension. Follow these rules so the generated reference pages stay
accurate. See [building-docs.md](building-docs.md) for the build itself.

## Style

- **Google style** only (`Args`, `Returns`, `Raises`, `Example`).
- Do not mix Sphinx fields (`:return:`, `:param:`) or roles (`:meth:`, `:class:`).
- Cross-reference with single backticks: `` `Palette` `` or
  `` `text <palettes.Palette.name>` ``. A single backtick in a docstring is a
  Python cross-reference. Use double backticks for code that is not a name.
- A blank line before every list, and a raw string or a doubled backslash for
  `\n` in prose: a bare `\n` in a normal docstring is a real newline and
  breaks the paragraph.
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
- **Private API:** Names starting with `_` are excluded from the API pages; minimal or no docstrings are fine.
  Document public methods that live on private implementation bases when they surface via inheritance
  (set `:inherited-members:` on the page for that class).
- **Properties:** write a sentence. Napoleon does not read `Name: text` on a
  property as a type, so the sentence stays a sentence.

## Types

Type information goes in the **docstring**, not the signature. These packages
run on MicroPython, where annotations cost bytecode and RAM.

Stubs are the planned answer for pip consumers who want real types — see
[Planned: type stubs](publishing-automation.md#planned-type-stubs-for-every-published-package).
Do not add `py.typed` to a package: it tells a type checker to trust inline
annotations that deliberately are not there.

## Verification

From the repo root, build the way CI does:

```bash
.venv-docs/bin/sphinx-build -W --keep-going -b html palettes/docs palettes/docs/_build/html
```

A docstring problem is a warning, and `-W` makes it a failure. Fix it before merging.

## Priority tiers

| Tier | Modules |
|------|---------|
| P0 | `displaydev`, `appdev`, `events`, `keys`, `multimer` |
| P1 | `displaybuf`, `console`, other `utils` |
| P2 | Sibling packages document their own APIs: [pygraphics](https://pygraphics.readthedocs.io), [pdwidgets](https://pdwidgets.readthedocs.io), [palettes](https://palettes.readthedocs.io) |

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the PR workflow, and
[building-docs.md](building-docs.md) for how the generated API pages are built.
