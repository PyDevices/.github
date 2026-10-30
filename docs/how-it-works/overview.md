# What this repository is

`PyDevices/.github` doesn't ship a product. It is what every other PyDevices
repository points at for the parts they'd otherwise duplicate. GitHub treats a
repository with this name specially: its community health files are the
defaults for any repository in the organization that doesn't have its own.

## What lives here

| Piece | Where | Read more |
|---|---|---|
| Community health defaults: contributing guide, code of conduct, security policy, support, pull request and issue templates | the root and `.github/ISSUE_TEMPLATE/` | [CONTRIBUTING.md](../../CONTRIBUTING.md) |
| The organization profile shown on github.com/PyDevices | `profile/README.md` | [where things live](../reference/github-org.md) |
| The reusable release workflows and the tag contract | `.github/workflows/reusable-*.yml`, `scripts/` | [the release chain](release-chain.md) |
| The release dashboard, one row per distribution | `RELEASE_HEALTH.md`, `release-health/data.json` | [fix a failed release](../guides/fix-a-failed-release.md) |
| The repository database and site generator | `data/repos_db.json`, `scripts/generate_sites.py` | [set up a checkout](../get-started/set-up.md) |
| The shared Sphinx configuration and the organization overview site | `docs-config/`, `docs-site/` | [build and publish documentation](../guides/build-and-publish-docs.md) |
| Shared standards | `docs/` | [design principles](design-principles.md), [platform support tiers](platform-support-tiers.md), [repository layout](../reference/repo-layout.md) |

`RELEASE_HEALTH.md` and `release-health/data.json` are written by the
`release-health` workflow on every release report, so don't edit them by hand.
Edit `data/repos_db.json` and run the generator rather than changing the pages
it produces. Other repositories' generated files are overwritten by their sync
scripts: change the generator, not the copy
([CONTRIBUTING.md](../../CONTRIBUTING.md#generated-files-and-sync-targets)).

## Where to start reading

To release a package, read [the release chain](release-chain.md) first, then
[release a package](../guides/release-a-package.md). To add a repository to the
organization's pages, edit the database and regenerate. To change how every
repository's documentation builds, start with the
[build guide](../guides/build-and-publish-docs.md).

A new maintainer reads [CONTRIBUTING.md](../../CONTRIBUTING.md), then the
README of the repository they will touch (each states its role and build path),
then [release a package](../guides/release-a-package.md) before their first
release.
