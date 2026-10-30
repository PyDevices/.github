# Where things live on GitHub

How the [PyDevices](https://github.com/PyDevices) organization is set up:
where to ask, where bugs go, and which pieces live in this repository. The
full list of repositories, grouped by tier, is generated from
`data/repos_db.json` and published as the
[ecosystem page](https://github.com/PyDevices/pydevices/blob/main/docs/how-it-works/ecosystem.md)
and on the [organization profile](https://github.com/PyDevices); this page
doesn't repeat it.

## Quick answers

| I want to... | Go here |
|---|---|
| Ask a question, propose an idea, show something I built, or reach the maintainer | [pydevices Discussions](https://github.com/PyDevices/pydevices/discussions), the organization's one board |
| Share a one-off example too narrow for the official examples | The *Recipes* category in [pydevices Discussions](https://github.com/PyDevices/pydevices/discussions) |
| Report a bug or ask for something that doesn't work yet | Issues on the repository it affects; the Bug report and Feature request templates apply by default |
| See what is planned | The `ROADMAP.md` at the root of each repository |
| Read the shared contribution guidelines | [CONTRIBUTING.md](../../CONTRIBUTING.md) |
| Read the organization's profile | [profile/README.md](../../profile/README.md), shown on [github.com/PyDevices](https://github.com/PyDevices) |
| Read a library's manual | The project's Read the Docs site, for example [pygraphics.readthedocs.io](https://pygraphics.readthedocs.io); the [documentation overview](https://pydevices.readthedocs.io) links the rest |
| Try the libraries without installing | The [PyScript gallery](https://pydevices.github.io/gallery/pyscript/) |
| Find board and driver documentation | [pydevices `docs/`](https://github.com/PyDevices/pydevices/tree/main/docs) |

## Discussions and issues

**Discussions** are on in one repository, `pydevices`: questions, ideas,
show-and-tell, and reaching the maintainer. Every other repository has them
off, so there is one place to look; `SUPPORT.md`, `CONTRIBUTING.md` and the
design docs all point there. Its *Recipes* category is a low-friction home for
one-off how-tos; one that gets traction can be promoted into a real example.

**Issues** are for bugs and for things you need that don't work yet. Planned
enhancements go in each repository's `ROADMAP.md` instead; a request that
becomes planned work moves there and its issue closes with a link. The default
issue templates (`bug.yml`, `feature.yml`) live in this repository's
[`.github/ISSUE_TEMPLATE`](../../.github/ISSUE_TEMPLATE) and apply to any
repository that doesn't define its own. If you aren't sure where an issue
belongs, open it on [pydevices](https://github.com/PyDevices/pydevices/issues)
and it will be routed.

**GitHub Projects** are off, so public work tracking is Issues, Discussions and
the roadmaps. **GitHub Packages** isn't used: installables go to TestPyPI and
PyPI for CPython, and to the `mip` and `lib` indexes for MicroPython.

## Read the Docs

Sphinx documentation for the organization overview, `pygraphics`, `palettes`
and `pdwidgets` publishes to Read the Docs as one site; see [build and publish
documentation](../guides/build-and-publish-docs.md). Read the Docs connects
through its [Community GitHub App](https://github.com/apps/read-the-docs-community),
installed on all of the organization's repositories (see the
[installed apps](https://github.com/organizations/PyDevices/settings/installations)),
so push and pull-request events arrive without a per-repository webhook. A new
project is imported from the Read the Docs dashboard, which lists repositories
through the app. A project still on a legacy webhook can
[migrate to the app](https://app.readthedocs.org/accounts/migrate-to-github-app/).
Each project's build is `.readthedocs.yaml` plus `docs/conf.py`, with no
secrets.

## Pages sites

Product repositories publish a landing page at `pydevices.github.io/<repo>/`
from the portal repository, [PyDevices.github.io](https://github.com/PyDevices/PyDevices.github.io).
This repository doesn't serve a Pages site of its own. The pages share one
chrome: `assets/css/site.css` and `assets/js/site-chrome.js` here are the
master copies, and the portal's `assets/chrome/` files are their sync targets.
Each page mounts empty `#pydevices-site-header` and `#pydevices-site-footer`
elements and the script fills them in; `theme-toggle.js` binds
`#theme-toggle`. Which pages exist, and where each is served, comes from
`data/repos_db.json` through `scripts/generate_sites.py`
([set up a checkout](../get-started/set-up.md#regenerate-the-org-sites)).

## Licensing

The organization's repositories are MIT, using GitHub's standard
single-author template, so GitHub detects it as MIT rather than
`NOASSERTION`. Keep the root `LICENSE` as the plain template: GitHub matches
it against the exact text, and even a short added paragraph can drop the match
below the confidence threshold. A few files carry code from other authors, for
example `gallery`'s `lib/utils/tft_text.py`, `tft_write.py` and `tft_bitmap.py`.
Those keep their own MIT header with the attribution, and the header governs
the file. New outside code is credited as described under [code from other
projects](repo-layout.md#code-from-other-projects).

## Topics

Each repository sets GitHub topics for discoverability (for example `lvgl`,
`micropython`, `circuitpython`). Read them in a repository's sidebar rather
than from a list here, which would go stale.
