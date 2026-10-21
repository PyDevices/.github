# pydevices-docs

The shared look and configuration of the PyDevices documentation projects: a
Sphinx theme (`sphinx_rtd_theme` with a PyDevices palette), the top bar that
links every project to every other, the Markdown setup, the Google-style
docstring setup, and the reference map between projects.

Each project's `docs/conf.py` calls `configure()` and sets only its name and
where its code is. This is what `palettes` does:

```python
from pydevices_docs import configure

globals().update(configure(
    "palettes", __file__,
    repo="PyDevices/pydevices", edit_path="palettes/docs",
    source_dirs=["../lib"], api_packages=["palettes"],
))
```

## Use it in a project

Put this line in the project's `docs/requirements.txt`, naming the release you
want:

```
pydevices-docs @ git+https://github.com/PyDevices/.github@docs-v0.1.0#subdirectory=docs-config
```

Then add `conf.py`, an `index.md`, and a `.readthedocs.yaml` that sets
`fail_on_warning: true`. Put a `reference/index` entry in a toctree to get
the API pages (see below).

## What `configure()` sets up

- Extensions: `myst_parser` (Markdown), `sphinx_design` (cards and tabs),
  `autodoc`, `napoleon` (Google style only), `intersphinx`, `viewcode`.
- API pages: with `api_packages=[...]`, one page per public module is written
  to `reference/` before each build, plus `reference/index.rst`. List
  `reference/` in the project's `.gitignore`.
- `mock_imports`: modules autodoc should not import (hardware modules a
  desktop build lacks).
- The reference map: the Python and MicroPython manuals, and every other
  PyDevices project whose `objects.inv` answers. A project that is not
  published yet is left out, so it cannot fail a `-W` build.
  `PYDEVICES_DOCS_OFFLINE=1` leaves all of them out.
- The version, read from the file named by `version_file` (default
  `../VERSION`).

## The top bar

`pydevices_docs/projects.py` lists the projects. A project is in the bar once
its `live` flag is true, which takes a new package release. Links are the Read
the Docs addresses; `pydevices-bar.js` rewrites them to the host serving the
page when that is the main project's site (or a subproject under it), so a
custom domain, a preview or a local server keeps readers where they are.

## Preview a project

```bash
python -m venv .venv-docs
.venv-docs/bin/pip install -r docs/requirements.txt
.venv-docs/bin/sphinx-build -W --keep-going -b html docs docs/_build/html
```

`sphinx-autobuild docs docs/_build/html` rebuilds as you edit.

## Live demos

A page can embed a runnable MicroPython demo: raw HTML in a Markdown page,
using the classes `pydevices-live-demo`, `demo-editor-pane`, `code-editor`,
`run-btn`, `reset-btn`, `demo-status`, `demo-output` and `demo-canvas-pane`
(this package styles them). The theme loads the runner,
`https://PyDevices.github.io/assets/chrome/docs-runtime.js`, on any page that
has one; the page needs no script tag. See the palettes `index.md` for a
complete demo.

## What moving the three MkDocs sites taught

- **A flag key is a flag.** In `autodoc_default_options`, `"ignore-module-all":
  False` turns the option on; leave the key out. `configure()` does.
- **Re-exports document twice.** A package that re-exports its names
  (`pdwidgets`, with lazy widgets) shows every class twice unless pages list
  only what a module defines. That is the default here. A package whose public
  names live in private modules (`pygraphics`) sets `use_module_all=True`.
- **Property docstrings.** Napoleon reads `Face style: flat or raised.` on a
  property as a type and a description, swapped. `configure()` turns that off
  for properties.
- **Write `\\n` in a docstring, or use a raw string.** A bare `\n` is a real
  newline, and the line after it falls out of the paragraph: a warning that
  `-W` turns into a failure.
- **Cross-references.** MkDocs docstrings used `[Name][path]`. Sphinx uses a
  single backtick (`default_role` is `py:obj`): `` `Name <path>` ``. The three
  libraries' docstrings were converted.
- **Links in Markdown.** MyST treats a link that starts with `/` as a
  cross-reference to a document. Link to another project with its full
  `https://` address.
- **Demos need no special headers.** They run with and without
  cross-origin isolation (COOP/COEP `credentialless`), which was checked with
  both. Setting COEP does block Read the Docs' own analytics beacon, so
  leave it off.
- **Docstring-only edits are enough.** The libraries' code did not change;
  only docstrings and the docs folder did.
