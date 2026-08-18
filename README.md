# .github

Org-wide community health files and profile for [PyDevices](https://github.com/PyDevices):

- [`profile/README.md`](profile/README.md) — the org profile page shown on [github.com/PyDevices](https://github.com/PyDevices).
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — shared contributing guide, used as the default for repos without their own.
- [`docs/repo-layout.md`](docs/repo-layout.md) — shared directory and root-file convention (`src` / `lib` / `tests` / `tools` / `requirements-dev.txt`, …), plus the preferred `MICROPYPATH` / `PYTHONPATH` search paths.
- [`data/repos_db.json`](data/repos_db.json) — **the single source of truth for the repository map**. [`scripts/generate_sites.py`](scripts/generate_sites.py) renders it into every landing page, into [`profile/README.md`](profile/README.md), and into [pydevices/docs/ecosystem.md](https://github.com/PyDevices/pydevices/blob/main/docs/ecosystem.md). Run it by hand from a full workspace checkout (`python3 dotgithub/scripts/generate_sites.py`) after editing the database; it validates the database first and is idempotent.
- [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/) — default bug report / feature request templates, used as the fallback for repos without their own.
- [`docs/github-presence.md`](docs/github-presence.md) — map of Discussions, Issues, Pages sites, licensing, and other org setup.
- [`docs/notes.md`](docs/notes.md) — Brad's personal working notes / todo list (not contributor-facing).
- [`docs/platform-feasibility-report.md`](docs/platform-feasibility-report.md) — platform feasibility analysis + org triage decisions (pursue / docs-only / out).
- [`docs/platform-roadmap.md`](docs/platform-roadmap.md) — cloud-agent workstreams for platform expansion (parallel pursue tracks, why-comment rule, out-of-scope list).
- [`docs/publishing-automation.md`](docs/publishing-automation.md) — shared release workflows, discovery rules, and the centralized MIP queue.
- [`docs/building-docs.md`](docs/building-docs.md) — how the three library ReadTheDocs sites (`palettes`, `pdwidgets`, `pygraphics`) are built and published.
- [`docs/docstrings.md`](docs/docstrings.md) — Google-style docstring conventions for the generated API reference pages.

Board / Detect inventory docs live in
[pydevices/docs](https://github.com/PyDevices/pydevices/tree/main/docs)
([Pages](https://pydevices.github.io/pydevices/)).

Website: <https://pydevices.github.io/>

This repo is the org-level glue for community health files, issue templates, and
shared docs. It does not publish a product Pages site of its own; the product
repos publish their own Pages content, while this repo provides the shared org
profile and documentation references.
