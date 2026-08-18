# Building and publishing documentation

How to preview a documentation site on your machine and publish it to
ReadTheDocs.

**This applies to the three library sites only** — `palettes`, `pdwidgets`, and
`pygraphics`. Every other PyDevices repository documents itself as plain
markdown browsed on github.com; do not add MkDocs to one.

| Repository | Site |
|---|---|
| [pygraphics](https://github.com/PyDevices/pygraphics) | [pygraphics.readthedocs.io](https://pygraphics.readthedocs.io) |
| [pdwidgets](https://github.com/PyDevices/pdwidgets) | [pdwidgets.readthedocs.io](https://pdwidgets.readthedocs.io) |
| [palettes](https://github.com/PyDevices/palettes) | [pydevices-palettes.readthedocs.io](https://pydevices-palettes.readthedocs.io) |

Docstring conventions for the generated API pages: [docstrings.md](docstrings.md).

## Preview locally

From the repository root:

```bash
python3 -m venv .venv-docs
.venv-docs/bin/pip install -r docs/requirements.txt
.venv-docs/bin/mkdocs serve
```

Open **http://127.0.0.1:8000** in your browser. MkDocs reloads when you edit files under `docs/`.

One-shot production build (output in `site/`):

```bash
.venv-docs/bin/mkdocs build
```

> **Already have the venv?**
>
> If `.venv-docs/` exists from a previous session, skip the `venv` and `pip install` lines and run `.venv-docs/bin/mkdocs serve` directly.

### What runs during a build

| File | Role |
|------|------|
| `mkdocs.yml` | Site config, theme, navigation |
| `docs/requirements.txt` | Python packages for MkDocs and plugins |
| `.readthedocs.yaml` | ReadTheDocs build settings (same deps) |
| `scripts/mkdocs_gen_ref_pages.py` | Auto-generates API reference stubs from source docstrings |

Hand-authored pages live under `docs/` and follow a **Try → Quick start → Install → Learn → Reference** structure (see `mkdocs.yml` nav).

API reference pages under `reference/` and `reference/utils/` are generated at build time — do not hand-edit them.

Shared copy-paste blocks: `docs/_snippets/` (included via pymdownx Snippets).

### Jupyter notebooks

Interactive Jupyter notebooks are generated on demand from example scripts using `jupyter.py`. See [pydevices/docs/jupyter.md](https://github.com/PyDevices/pydevices/blob/main/docs/jupyter.md).

### Troubleshooting

**`ModuleNotFoundError` during build** — use a venv as shown above; do not `pip install` into the system Python on Debian/Ubuntu (externally-managed-environment error).

**Griffe warnings** — docstring parameter mismatches in source; warnings only, build still succeeds.

**MkDocs 2.0 warning banner** — harmless; set `DISABLE_MKDOCS_2_WARNING=true` to hide it.

#### ReadTheDocs: "Builds disabled due to consecutive failures"

This project was registered on ReadTheDocs before the docs revamp. RTD kept building **`main`**, which had broken MkDocs config (missing nav pages, no `docs/requirements.txt`, wrong mkdocstrings paths). After 25 failures, RTD auto-disabled builds.

**Fix:**

1. **Admin** → **Settings** → Advanced → uncheck **Disable builds for this project** → Save.
2. **Push fixes to `main`** — RTD builds from the default branch; it cannot build changes that exist only locally.
3. **Admin** → **Versions** → ensure **`latest`** is active → click **Build version**.
4. Confirm the build log shows MkDocs Material and `docs/requirements.txt` installing — not the old readthedocs theme with missing `test2.md`.

#### ReadTheDocs: "Search indexing has been disabled"

Harmless for now — RTD pauses search indexing on inactive projects. After docs are live and receiving traffic:

**Admin** → **Settings** → **Enable search indexing** → Save.

---

## Publish to ReadTheDocs

ReadTheDocs reads `.readthedocs.yaml` from the repository and runs the same MkDocs build as locally.

### Org GitHub App (required)

PyDevices uses the
[Read the Docs Community GitHub App](https://github.com/apps/read-the-docs-community)
installed on the org with access to **all repositories** (see
[org installation](https://github.com/organizations/PyDevices/settings/installations)).
That app delivers push/PR events to RTD — do **not** add a manual
`readthedocs.org/api/v2/webhook/...` hook on the repo.

Docs projects on the same app: **pygraphics**,
**palettes**, **pdwidgets**.

### First-time setup (new project)

1. Go to [readthedocs.org](https://readthedocs.org) and sign in with **GitHub**
   (an account that can see the repository).
2. Open the [Read the Docs dashboard](https://app.readthedocs.org/dashboard/)
   and click **Add project**.
3. Search for the repository under **`PyDevices/`** and import it.
   - If the repo does not appear, confirm the
     [GitHub App installation](https://github.com/organizations/PyDevices/settings/installations)
     includes this repository, then use **Refresh your repositories** on RTD.
4. On the setup form, confirm:
   - **Documentation type:** MkDocs (auto-detected from `.readthedocs.yaml`)
   - **Configuration file:** `.readthedocs.yaml`
   - Click **Next**, then **This file exists** (the config is already in the repo).
5. **Build `latest` (tracks `main`):**
   - Go to **Admin** → **Versions**.
   - Ensure **`latest`** is **Active** and set as the **default version**.
   - Click **Build** on `latest` (or wait for the next push to `main`).
6. Check the **Builds** tab. A successful build ends with
   `Documentation built successfully`. The site appears at:
   - `https://<project>.readthedocs.io/en/latest/`
   - `https://<project>.readthedocs.io/` when `latest` is the default

### Migrating a legacy (webhook) project to the GitHub App

Older imports used a per-repo webhook under GitHub **Settings → Webhooks**.
Those PyDevices docs projects (**pygraphics**, **palettes**, **pdwidgets**) have
been migrated to the org GitHub App via
[Migrate to GitHub App](https://app.readthedocs.org/accounts/migrate-to-github-app/);
legacy webhooks are removed. New projects should use the App from the start
(no manual webhook).

### Ongoing

1. RTD rebuilds automatically when you push to `main` (via the GitHub App).
2. Optionally disable obsolete version slugs under **Admin** → **Versions** if any remain from earlier experiments.
3. Enable **search indexing** under **Settings** once the site is live.

### Optional: pull request previews

In RTD project **Admin** → **Preview documentation from pull requests**, enable PR builds so each PR gets a preview URL before merge.

## Check GitHub Actions from the CLI

Authenticate once (stores credentials for future sessions):

```bash
gh auth login
```

Then from the repo root:

```bash
gh run list --limit 5              # recent workflow runs
gh run watch                       # follow the latest run
```

Useful after pushing doc changes to confirm the RTD build succeeded.
