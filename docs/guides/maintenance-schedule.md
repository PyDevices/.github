# Keep to the maintenance schedule

Most upkeep runs by itself. This page lists what runs when, so you know which
red run is routine and which job is yours.

## Continuous

- **Release Health.** Every publish run reports, pass or fail, to
  [`RELEASE_HEALTH.md`](../../RELEASE_HEALTH.md).
- **This repository's checks.** Every push and pull request runs actionlint,
  the YAML and tag-reference checks, the site generator's idempotency check,
  `ruff`, the script tests and the docs build
  ([`checks.yml`](../../.github/workflows/checks.yml)).
- **Each repository's own CI**, on every push.

## Daily

- **Hero check** (06:41 UTC,
  [`hero-check.yml`](../../.github/workflows/hero-check.yml)). Loads the
  published demos in a browser and opens an issue when one stops running. The
  page can render while its demo is dead, so nothing else notices.

## Weekly, Mondays

- **Font drift** in `omnipython-lvgl` (06:17 UTC). Regenerates the font
  binaries and fails when they differ from the committed ones.
- **Overlay compatibility** in `micropython-pydevices` (06:43 UTC). Applies
  every profile to the pinned upstream and fails when one no longer applies.
- **Firmware build** in `micropython-pydevices` (05:17 UTC). Builds every
  firmware image without publishing anything, which keeps the caches warm and
  shows the week an upstream pin moves and a board stops building.

On Wednesdays (04:41 UTC) `micropython-pydevices` also rebuilds each
dev container from nothing, as a codespace would.

Dependabot opens one grouped pull request a week per repository for pinned
action versions.

## Monthly, by hand

- Merge the month's Dependabot pull requests. They arrive grouped.
- Skim the TestPyPI project pages for anything you don't recognise.
- Check upstream MicroPython releases. A new stable release is information,
  not an obligation: moving a pin (the MicroPython base, the LVGL submodule,
  PyScript, the CircuitPython oracle) is deliberate work with its own
  verification.

## Quarterly

- **Cold-eyes review** ([`cold-eyes-review.yml`](../../.github/workflows/cold-eyes-review.yml)).
  On the first of January, April, July and October it opens an issue naming
  three repositories from a rotating list, with four checks to re-run on each:
  a clean build from the README, the README to a working example on a first
  try, a `.devN` release through the whole chain, and a walk through the org's
  front door (portal, cards, links, a 404). File what you find as issues on
  the affected repositories.
- Review whether the CircuitPython version `audiodsp` pins should move. It
  stays put until moving it is its own piece of work.
