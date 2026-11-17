# Build and publish documentation

How the OmniPython documentation site is built from every library's own
`docs/` folder, how to preview it, and how a change in a library reaches Read
the Docs.

There is one site and one Sphinx build. Its source is [docs-site/](../../docs-site/)
here: the front pages, and [libraries.toml](../../docs-site/libraries.toml), the
list of libraries in sidebar order. Each library's pages stay in its own
repository, beside a `conf.py` that builds them alone. Before the build,
[gather.py](../../docs-site/gather.py) clones each repository's `main` and
copies its docs folder in as a section, so the site has one search, one table
of contents and one sidebar. The shared theme and configuration are the
`omnipython-docs` package, [docs-config/](../../docs-config/).

| Section | Source |
|---|---|
| The front pages | [docs-site/](../../docs-site/) here |
| `/omnipython/`, `/palettes/`, `/pdwidgets/` | `docs/`, `packages/palettes/docs/`, `packages/pdwidgets/docs/` in [omnipython](https://github.com/PyDevices/omnipython) |
| `/pygraphics/` | `docs/` in [pygraphics](https://github.com/PyDevices/pygraphics) |
| `/lvgl/` | `docs/` in [omnipython-lvgl](https://github.com/PyDevices/omnipython-lvgl) |
| `/audiodsp/`, `/audioinstruments/`, `/audioeffects/` | `docs/` in each repository |
| `/firmware/` | `docs/` in [omnipython-builds](https://github.com/PyDevices/omnipython-builds) |

Docstring conventions for the generated API pages: [write docstrings](write-docstrings.md).

## Preview the site

From this repository's root:

```bash
python3 -m venv .venv-docs
.venv-docs/bin/pip install -r docs-site/requirements.txt
.venv-docs/bin/python docs-site/gather.py
.venv-docs/bin/sphinx-build -b html --keep-going -w warnings.log docs-site docs-site/_build/html
.venv-docs/bin/python docs-site/check_warnings.py warnings.log
```

The build takes about a minute. To see a library change before it is pushed,
gather from your checkout instead of a clone, and run `gather.py` again after
each edit: `gather.py --local pygraphics=../pygraphics`. Serve the result with
`python3 -m http.server -d docs-site/_build/html`; live demos need http, not
`file://`.

## Preview one library alone

Each library still builds alone from its own repository, which is quicker and
is what its own CI checks with `-W`:

```bash
python3 -m venv .venv-docs
.venv-docs/bin/pip install -r docs/requirements.txt
.venv-docs/bin/sphinx-build -W --keep-going -b html docs docs/_build/html
```

`requirements.txt` installs a tagged `omnipython-docs`. To work on the shared
package, install your checkout instead:
`.venv-docs/bin/pip install -e <path to this repository>/docs-config`. No
network? Set `OMNIPYTHON_DOCS_OFFLINE=1`.

## How a library's conf.py is read

The library's `conf.py` is the one description of how its pages are built,
alone and on the site. The site runs it from the clone and keeps what it
passes to `omnipython_docs.configure()` (import folders, API packages, mocks,
`__all__` or not), plus `master_doc`, `exclude_patterns`, `suppress_warnings`
and `myst_heading_anchors`, and calls its `setup(app)` with the section's
folder as `app.srcdir`. While Sphinx reads a page, the mocks and autodoc
defaults are that page's library's, so libraries that mock each other's
modules build as they do alone. The details are in
[site.py](../../docs-config/src/omnipython_docs/site.py).

A library whose `master_doc` is a navigation page (`contents.md`) starts at
its `index` on the site, and the navigation's toctrees move onto that page.
Links and includes that leave the docs folder (`../src/x.c`,
`../CHANGELOG.md`) are pointed back at the repository.

## Warnings

A warning on the site belongs to the repository whose file caused it, and it
fails that repository's check, not anyone else's. Read the Docs builds with
`fail_on_warning: false`, so one library's bad page shows as it is (and in the
build log) rather than stopping every other library's update.

- Each library's own docs job builds it alone with `-W`, on every pull request.
- Each library's **Docs site** workflow builds the whole site with the
  pull request's pages in it, and fails when that library has a warning there.
  The annotations land on the library's files.
- This repository's `docs-site` check does the same for the front pages and the
  shared package, and prints every library's count.

### Troubleshooting

**`ModuleNotFoundError` while importing a module for the API pages**: autodoc
imports the package. Name modules a desktop build lacks (hardware, interpreter
builtins) in `mock_imports` in the library's `conf.py`.

**A docstring warning fails the build**: fix it in the docstring, not the
signature. These packages run on MicroPython and CircuitPython, where
annotations cost bytecode and RAM. See [write docstrings](write-docstrings.md).

**An API page is missing a name**: the page documents what the module
defines. For a package whose public names live in private modules (pygraphics),
set `use_module_all=True` so the page follows `__all__`.

## The tools' site

The tools a person runs (MCU Control, mpvst and Workbench) have a second site,
docs.pydevices.com, built the same way from [tools-docs-site/](../../tools-docs-site/):
its own front page and [libraries.toml](../../tools-docs-site/libraries.toml),
the same `gather.py` and theme, with the PyDevices name and mark in the bar.
Pass `--site tools-docs-site` to each step:

```bash
.venv-docs/bin/pip install -r tools-docs-site/requirements.txt
.venv-docs/bin/python docs-site/gather.py --site tools-docs-site
.venv-docs/bin/sphinx-build -b html --keep-going -w warnings.log tools-docs-site tools-docs-site/_build/html
.venv-docs/bin/python docs-site/check_warnings.py warnings.log --site tools-docs-site
```

It is its own Read the Docs project, whose **Path for .readthedocs.yaml** is
[tools-docs-site/.readthedocs.yaml](../../tools-docs-site/.readthedocs.yaml).
A tool's **Docs site** workflow passes `site: tools-docs-site` to the reusable
workflow, with that project's webhook as `RTD_TOOLS_WEBHOOK_URL` and
`RTD_TOOLS_WEBHOOK_TOKEN`.

## Publish to Read the Docs

The site is the Read the Docs project `pydevices`, built from this repository
by the root [.readthedocs.yaml](../../.readthedocs.yaml), which runs
`gather.py` before Sphinx. Readers land on **latest**, built from `main`.

Read the Docs rebuilds on a push here through the org's
[Read the Docs Community GitHub App](https://github.com/apps/read-the-docs-community).
A push to a library's `main` doesn't reach this repository, so each library's
**Docs site** workflow calls the project's incoming build webhook after a push
that touches its docs or the code they're generated from. It needs the
organization secret `RTD_WEBHOOK_TOKEN` and the organization variable
`RTD_WEBHOOK_URL`, both from the project's **Admin > Integrations > Generic
API incoming webhook**. Without them the workflow says so in a notice and
skips the call; the site then catches up on the next build here.

### A new library

1. Give it a `docs/` folder with a `conf.py` that calls
   `omnipython_docs.configure()`, and build it alone with `-W`.
2. Add it to [libraries.toml](../../docs-site/libraries.toml) and to
   [docs-site/.gitignore](../../docs-site/.gitignore).
3. Copy the caller workflow from another library
   (`.github/workflows/docs-site.yml`) and set its paths.
