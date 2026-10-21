# Building and publishing documentation

How to preview a PyDevices documentation project on your machine and how it
reaches Read the Docs.

One Sphinx configuration, in the `pydevices-docs` package
([docs-config/](../docs-config/)), gives every project the same theme, the
same top bar linking every project to every other, and the same Markdown and
docstring setup. The organization overview is the main project, built from
[docs-site/](../docs-site/); each library's manual is a subproject.

| Project | Source | Site |
|---|---|---|
| PyDevices (the main project) | [docs-site/](../docs-site/) here | `pydevices.readthedocs.io` |
| palettes | [palettes/docs](https://github.com/PyDevices/pydevices/tree/main/palettes/docs) | `/projects/palettes/` under the main site |
| pdwidgets | [pdwidgets/docs](https://github.com/PyDevices/pydevices/tree/main/pdwidgets/docs) | `/projects/pdwidgets/` |
| pygraphics | [docs/](https://github.com/PyDevices/pygraphics/tree/main/docs) in its repo | `/projects/pygraphics/` |

Docstring conventions for the generated API pages: [docstrings.md](docstrings.md).

## Preview locally

From the project's repository root (for palettes and pdwidgets, from the
`pydevices` checkout):

```bash
python3 -m venv .venv-docs
.venv-docs/bin/pip install -r palettes/docs/requirements.txt   # or pdwidgets/, or docs/ in pygraphics
.venv-docs/bin/sphinx-build -W --keep-going -b html palettes/docs palettes/docs/_build/html
```

`requirements.txt` installs the tagged `pydevices-docs`. To work on the shared
package itself, install your checkout instead:
`.venv-docs/bin/pip install -e ../.github/docs-config`.

Open `_build/html/index.html`, or serve the folder
(`python3 -m http.server -d palettes/docs/_build/html`). Live demos need http,
not `file://`. `sphinx-autobuild palettes/docs palettes/docs/_build/html`
rebuilds as you edit.

`-W` turns every warning into a failure. That is how CI and Read the Docs
(`fail_on_warning: true` in `.readthedocs.yaml`) build, so a build that passes
here passes there. No network? Set `PYDEVICES_DOCS_OFFLINE=1` to skip the
reference map to the Python and MicroPython manuals.

### What runs during a build

| File | Role |
|------|------|
| `docs/conf.py` | Five lines: the project's name and where its code is, passed to `pydevices_docs.configure()` |
| `docs/requirements.txt` | The pinned `pydevices-docs` release |
| `.readthedocs.yaml` | Read the Docs build settings |
| `docs/reference/` | API pages, written at build time from the package's modules (git-ignored) |

Hand-authored pages are Markdown (MyST) in `docs/`. Cards and tabs come from
`sphinx-design`, diagrams from `mermaid`, and the live browser demos are raw
HTML (see the [pydevices-docs README](../docs-config/README.md)).

### Troubleshooting

**`ModuleNotFoundError` while importing a module for the API pages** -- autodoc
imports the package. Name modules a desktop build lacks (hardware, interpreter
builtins) in `mock_imports` in `conf.py`.

**A docstring warning fails the build** -- fix it in the **docstring**, not the
signature: these packages run on MicroPython and CircuitPython, where
annotations cost bytecode and RAM. See [docstrings.md](docstrings.md).

**An API page is missing a name** -- the page documents what the module
defines. For a package whose public names live in private modules (pygraphics),
set `use_module_all=True` so the page follows `__all__`.

## Publish to Read the Docs

Read the Docs reads `.readthedocs.yaml` from the repository. The main project
and each subproject are separate Read the Docs projects; the main project lists
the others under **Subprojects**, which is what puts them at
`/projects/<name>/` and gives every page the same address scheme.

### Org GitHub App

PyDevices uses the
[Read the Docs Community GitHub App](https://github.com/apps/read-the-docs-community)
installed on the org with access to all repositories (see the
[org installation](https://github.com/organizations/PyDevices/settings/installations)).
It delivers push and pull-request events; do not add a manual
`readthedocs.org/api/v2/webhook/...` hook.

### A new project

1. Open the [Read the Docs dashboard](https://app.readthedocs.org/dashboard/)
   and **Add project**; pick the repository under `PyDevices/`.
2. If the project's `.readthedocs.yaml` is not at the repository root, set
   **Settings > Advanced > Path for .readthedocs.yaml** (palettes and pdwidgets
   use `palettes/.readthedocs.yaml` and `pdwidgets/.readthedocs.yaml`).
3. Make sure `latest` (tracking `main`) is active and the default version.
4. On the main project, **Subprojects > Add subproject**, with the project's
   name as the alias.
5. Add the project to `projects.py` in `docs-config/` with `live = True` and
   release a new `pydevices-docs`, so it appears in every project's top bar.

### Versions

Readers land on **latest**, built from `main`. Keep only the most recent
release version active beside it (**Admin > Versions**); hide the rest.

### Pull request previews

In the project's **Admin > Preview documentation from pull requests**, enable
PR builds so each PR gets a preview before merge.
