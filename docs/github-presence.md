# PyDevices on GitHub — feature reference

A map of how the [PyDevices](https://github.com/PyDevices) GitHub org is set
up: where discussions, issues, docs, and Pages sites live. Written to answer
"how do I...?" / "where do I find...?" questions later without re-deriving
the answer from scratch.

## Quick answers

| I want to... | Go here |
|---|---|
| Ask a question / propose an idea / show something I built | [pydevices-examples Discussions](https://github.com/PyDevices/pydevices-examples/discussions) |
| Find or share a one-off example that's too narrow for the official examples | [pydevices-examples Discussions → Recipes](https://github.com/PyDevices/pydevices-examples/discussions/categories/recipes) |
| Report a bug or request a feature | Issues on the **specific repo** it affects (see [repo map](#repos--pages-sites)); use the Bug report / Feature request templates |
| Find contribution guidelines shared across repos | [PyDevices/.github CONTRIBUTING.md](https://github.com/PyDevices/.github/blob/main/CONTRIBUTING.md) |
| Read the org's public-facing "about us" | [PyDevices/.github profile README](https://github.com/PyDevices/.github/blob/main/profile/README.md) (rendered on [github.com/PyDevices](https://github.com/PyDevices)) |
| Read pydevices-examples documentation | [pydevices-examples/docs](https://github.com/PyDevices/pydevices-examples/tree/main/docs) |
| Read pygraphics documentation | [pygraphics.readthedocs.io](https://pygraphics.readthedocs.io) |
| Read palettes / pdwidgets docs | [palettes.readthedocs.io](https://palettes.readthedocs.io), [pdwidgets.readthedocs.io](https://pdwidgets.readthedocs.io) |
| Manage Read the Docs ↔ GitHub (org app) | [Read the Docs Community GitHub App](https://github.com/organizations/PyDevices/settings/installations/149173814) (all repos); migrate legacy projects at [RTD migrate-to-github-app](https://app.readthedocs.org/accounts/migrate-to-github-app/) |
| Try the library without installing anything | [PyScript browser demos](https://pydevices.github.io/pydevices-examples/pyscript/) |
| Hardware board/driver docs (configs, contract, drivers, matrix) | [pydevices Pages](https://pydevices.github.io/pydevices/) ([docs/](https://github.com/PyDevices/pydevices/tree/main/docs)) |
| Talk to a board from VS Code / Cursor (REPL, files, firmware) | [mpftp](https://github.com/PyDevices/mpftp) ([Pages](https://pydevices.github.io/mpftp/); agent state under `~/.mpftp/`) |

## Getting help: Discussions vs. Issues

- **Discussions** are enabled only on **pydevices-examples** and **lvgl-bindings** (the
  two repos most likely to get open-ended questions). Everything else routes
  through pydevices-examples Discussions — see the org's pinned "get help" pointer.
- **Issues** are enabled on every owned repo (bug reports / feature requests).
  Default issue *templates* (`bug.yml`, `feature.yml`) live in the org's
  [`.github`](https://github.com/PyDevices/.github/tree/main/.github/ISSUE_TEMPLATE)
  repo and apply automatically to any repo that doesn't define its own.
- If you're not sure which repo an issue belongs to, open it on
  [pydevices-examples](https://github.com/PyDevices/pydevices-examples/issues) — per
  CONTRIBUTING.md, that's the routing point.
- **Recipes** ([pydevices-examples Discussions → Recipes](https://github.com/PyDevices/pydevices-examples/discussions/categories/recipes),
  open-ended format, not answerable) is for one-off examples/how-tos that
  answer a specific question well but are too narrow to promote into
  `src/examples/`. If one gets enough traction, promote it into a real
  example later — this category is meant to be a low-friction incubator,
  not a permanent home for everything filed into it.
- **Wikis** are disabled org-wide — reference content lives in each repo's
  `README.md`/`AGENTS.md`, in
  [pydevices-examples documentation](https://github.com/PyDevices/pydevices-examples/tree/main/docs), or on a Pages site,
  not in a wiki page.
- **Projects** are disabled org-wide (org boards and per-repo Projects). Public
  work tracking is Issues + Discussions; there is no org kanban.
- **GitHub Packages** is not used. Installables go to TestPyPI / PyPI (CPython)
  and [micropython-lib](https://github.com/PyDevices/mip) via `mip`
  (MicroPython) — not GHCR or other GitHub package registries.

## Org profile

- **About / description / website**: set on the org (`https://pydevices.github.io/`).

## Read the Docs

MkDocs sites for **pydevices-examples**, **pygraphics**, **palettes**, and **pdwidgets**
publish to `*.readthedocs.io`. GitHub integration uses the org-installed
[Read the Docs Community](https://github.com/apps/read-the-docs-community)
app (**all repositories** — installation
[149173814](https://github.com/organizations/PyDevices/settings/installations/149173814)).

With the GitHub App, RTD receives push/PR events directly — no per-repo webhook
is required. The docs repos (**pydevices-examples**, **pygraphics**, **palettes**,
**pdwidgets**) use this app; legacy `api/v2/webhook/...` hooks are gone. New
projects: import from the RTD dashboard (repo list comes from the app). If an
older project still needs migrating:
[Migrate to GitHub App](https://app.readthedocs.org/accounts/migrate-to-github-app/).

Build config in each docs repo is `.readthedocs.yaml` + `mkdocs.yml` (no secrets).

## Repos & Pages sites

Every product and module repo below ships a GitHub Pages site sharing the same
chrome (dark-default theme, light toggle in the header, PyDevices brand linking
to the org root) from
[PyDevices.github.io](https://github.com/PyDevices/PyDevices.github.io)'s
`assets/css/site.css` and `assets/js/site-chrome.js`. Pages mount empty
`#pydevices-site-header` / `#pydevices-site-footer` elements; the script injects
identical markup (nav: Gallery, Examples, DisplayIF, Drivers, GitHub) and
`theme-toggle.js` binds `#theme-toggle`. The shared org site is the exception:
[PyDevices/.github](https://github.com/PyDevices/.github)
provides org metadata and docs, but it does not publish a product Pages site of
its own. Per-repo Pages heroes use marks under `assets/img/products/*.svg` (or
the repo's own `web/img/product.svg`); the org landing cards use compact inline
icons. Header brand stays on the shared org logo.

| Repo | Role | Pages site |
|---|---|---|
| [pydevices-examples](https://github.com/PyDevices/pydevices-examples) | Examples, tutorials, and PyScript showcase for the PyDevices product stack | [pydevices.github.io/pydevices-examples](https://pydevices.github.io/pydevices-examples/) (+ [PyScript demos](https://pydevices.github.io/pydevices-examples/pyscript/)) |
| [palettes](https://github.com/PyDevices/palettes) | Color palette toolkit for PyDevices | [pydevices.github.io/palettes](https://pydevices.github.io/palettes/) |
| [pdwidgets](https://github.com/PyDevices/pdwidgets) | Cross-platform widget toolkit for PyDevices | [pydevices.github.io/pdwidgets](https://pydevices.github.io/pdwidgets/) |
| [lvgl-bindings](https://github.com/PyDevices/lvgl-bindings) | LVGL C→binding generator (source of truth for the native cmods) | [pydevices.github.io/lvgl-bindings](https://pydevices.github.io/lvgl-bindings/) |
| [cmods](https://github.com/PyDevices/cmods) | Optional workspace for multi-usermod MicroPython/CircuitPython builds | *(no Pages site — org landing card links to the repo)* |
| [displayif](https://github.com/PyDevices/displayif) | Native display bus/framebuffer modules | [pydevices.github.io/displayif](https://pydevices.github.io/displayif/) |
| [pygraphics](https://github.com/PyDevices/pygraphics) | Native + pure-Python FrameBuffer/Area (`import pygraphics`); docs on [RTD](https://pygraphics.readthedocs.io) | [pydevices.github.io/pygraphics](https://pydevices.github.io/pygraphics/) |
| [lvgl-micropython](https://github.com/PyDevices/lvgl-micropython) | MicroPython user C module glue for LVGL | [pydevices.github.io/lvgl-micropython](https://pydevices.github.io/lvgl-micropython/) |
| [lvgl-circuitpython](https://github.com/PyDevices/lvgl-circuitpython) | CircuitPython integration for LVGL | [pydevices.github.io/lvgl-circuitpython](https://pydevices.github.io/lvgl-circuitpython/) |
| [lvgl-python](https://github.com/PyDevices/lvgl-python) | Native CPython LVGL extension (`import lvgl`) | [pydevices.github.io/lvgl-python](https://pydevices.github.io/lvgl-python/) |
| [pydevices-android-template](https://github.com/PyDevices/pydevices-android-template) | Native Android APK application template for PyDevices | [pydevices.github.io/pydevices-android-template](https://pydevices.github.io/pydevices-android-template/) |
| [pydevices-pyscript-template](https://github.com/PyDevices/pydevices-pyscript-template) | Minimal installable PyScript/PWA application template | [pydevices.github.io/pydevices-pyscript-template](https://pydevices.github.io/pydevices-pyscript-template/) |
| [PyDevices.github.io](https://github.com/PyDevices/PyDevices.github.io) | Org landing + shared chrome | [pydevices.github.io](https://pydevices.github.io/) |
| [.github](https://github.com/PyDevices/.github) | This repo — org profile README, issue templates, CONTRIBUTING.md, `docs/github-presence.md`, `docs/repo-layout.md`, `docs/notes.md` | *(no Pages site — org metadata only)* |
| [micropython-lib](https://github.com/PyDevices/mip) | Fork carrying PyDevices' micropython-lib packages for `mip install` | *(no dedicated marketing site — it's a package index fork, not a product)* |
| [pydevices](https://github.com/PyDevices/pydevices) | Canonical reusable product: cross-runtime libraries, board configs, and hardware drivers published for pip and MIP | [pydevices.github.io/pydevices](https://pydevices.github.io/pydevices/) |
| [mpftp](https://github.com/PyDevices/mpftp) | VS Code / Cursor board tools (REPL, file transfer, mip/circup, MicroPython firmware) | [pydevices.github.io/mpftp](https://pydevices.github.io/mpftp/) |

## Licensing

All owned repos are **MIT**, using GitHub's standard single-author template
(so it's correctly detected as MIT rather than `NOASSERTION`/`Other`). A
handful of files in **pydevices-examples** that still carry code from other authors
(`src/utils/tft_text.py`, `tft_write.py`, `tft_bitmap.py`, and the
`polygon()` function in `PyDevices/pygraphics`'s `lib/pygraphics/_shapes.py`, tracing back through
Russ Hughes' st7789_mpy driver to Ivan Belokobylskiy's st7789py_mpy) keep
their own self-contained MIT header with that attribution — those in-file
notices govern those specific files/functions; the root `LICENSE` governs
everything else. Keep any such pointer *out* of the root `LICENSE` file
itself: GitHub's license detector does a similarity match against the exact
template, and extra text (even a short explanatory paragraph) can drop it
below the confidence threshold and flip the repo back to `NOASSERTION`.

## Topics

Each repo has GitHub topics set for discoverability (e.g. `lvgl`,
`micropython`, `circuitpython`, `user-c-modules`) — check a repo's sidebar on
github.com rather than duplicating the list here, since topics change more
often than this doc will be updated.
