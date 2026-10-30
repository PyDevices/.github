# The release chain

This is how a package version gets from a merged pull request to TestPyPI,
the MIP index, the library index and, for some packages, production PyPI. The
organization-wide release machinery lives in this repository because it
governs every publishing repository: the reusable workflows, the tag contract
and the shared credentials. Each repository's own publishing notes cover only
what its release produces, such as `pydevices`'s dynamically discovered
package set. They add build and test detail; they don't replace what's here.

To run a release, see [release a package](../guides/release-a-package.md). For
the tables of inputs, secrets and tags, see
[release workflows](../reference/release-workflows.md).

## The release event

A published GitHub Release named `vX.Y.Z` is the authoritative event. The tag
selects the exact files to build and `X.Y.Z` becomes the package version. A
manual run only retries an existing tag.

Choosing the version is the organization's one deliberate exception to full
automation. The chain removes the manual tag, push and release steps around
that choice:

1. **Prepare release** (`workflow_dispatch`) opens a pull request that carries
   `VERSION` and `CHANGELOG.md`.
2. A person confirms or edits the version on that pull request and merges it.
3. **Tag release** sees the merged `VERSION` change on `main` and creates the
   tag and the GitHub Release, using the GitHub App's token. The token matters:
   a Release made with the default `GITHUB_TOKEN` doesn't trigger
   `on: release` workflows, so the publish run would never start.
4. **Publish release packages** runs on the Release event.

## How the publish run is wired

`reusable-publish-release-packages.yml` is the whole per-repository chain, as
jobs inside one reusable workflow. It resolves the tag, runs exactly one build
(`build-pure-python`, `build-native-and-wasm` or `build-pydevices-multi`,
chosen by `build-kind`), uploads to TestPyPI, attaches the built files to the
Release, requests MIP and library-index publication, decides whether
production PyPI should follow, and reports to the Release Health dashboard.
It replaced five near-identical copies of the same three jobs. The production
PyPI upload is the one step that has to live in the caller
([why](../guides/publish-to-pypi.md#why-the-upload-is-in-the-caller)).

Each publishing repository has thin callers (`prepare-release.yml`,
`tag-release.yml`, `publish-release-packages.yml`) that each call one reusable
workflow and supply only what differs.
[Workflows](../reference/workflows.md) lists the callers and what each passes.

Some repositories wrap the chain in more jobs. `audiodsp` runs parity gates
and a credentials check first, and an `expected-wheel-count` that has to follow
`requires-python` by hand. `audiocomponents` runs its own gates against the
core it pins, then two `pure-python` builds from `lib/audioinstruments` and
`lib/audioeffects`; both MIP entries ride on the first job's comma-separated
`mip-profile`, since both come from one tag.

Changing a reusable workflow's contract is an automation rollout, not a
package release. Validate it on its own, cut a new publishing tag, move the
callers deliberately, and only then use that tag for package versions.

## The tag contract

A caller pins a reusable workflow at a tag, not a branch:

```yaml
uses: PyDevices/.github/.github/workflows/reusable-publish-release-packages.yml@publishing-vN
```

A change here therefore doesn't alter any release until a caller moves its
tag. The tags are immutable by policy and by an active tag ruleset that blocks
moving or deleting one: a bad tag is fixed by a new one.

The coordinator also calls four sibling reusables, and those calls name the
same tag by full path. A local `./` path doesn't work: in a called workflow it
resolves against the consumer's repository, so the consumer's run dies at
startup with no jobs. Three reusables also check out this repository's
`scripts/` at `publishing-tools-ref`, so that default has to name the same tag
too. Keeping every one of those references equal to the tag being cut is
mechanical work, which is why `scripts/cut_publishing_tag.sh` is the only way
a tag is cut: it rewrites them all, commits that one change and tags the same
commit. The `sibling-refs` job in `checks.yml` refuses a tree where any
disagree or use `./`.

## What the `pydevices` release contains

The `pydevices` build keeps no inclusion list. The distribution is exactly
`lib/`, though the two ecosystems package it differently:

- **One package in each.** On PyPI it's the `pydevices` distribution; on MIP
  the `pydevices` package. A package per component was tried and dropped:
  micropython-lib resolves `require()` by inclusion at build time rather than
  as a dependency edge, so each package that required `events.py` carried its
  own copy and installing two wrote the file twice.
- **A microcontroller gets only what can run on one.** `displaydev`, `audiodev`
  and `multimer` each carry platform backends, many of them desktop, browser or
  Android code. The source repository's `mip-split.toml` names the host-only
  modules; they ship in `pydevices-desktop` instead, and `pydevices` lists its
  files one by one so the install list is the manifest. A name in the file that
  no longer exists fails the sync, and so does a device-side module that
  imports a host-only one at module scope. A new backend nobody classified
  ships to the device, so forgetting costs one extra file on a board, never a
  missing import on a host.
- **A package can publish to MIP on its own.** A `mip-split.toml` section with
  `own-package = true` leaves the `pydevices` package and becomes a sibling at
  `micropython/pydevices/<name>`, with its own `requires` as `require()` lines.
  `bledev` is one: a board without a radio doesn't carry BLE. On PyPI the code
  stays in the `pydevices` wheel, and `pypi-extras` makes an extra such as
  `pip install "pydevices[ble]"`.
- **A top-level directory can publish under its own name.** A section that is
  only `top-level = true` publishes `<repo>/<name>/` to
  `micropython/pydevices/<name>`, with the directory's `manifest.py` as the
  single source for its description, `require()` lines and files. The sync
  fails if a listed name isn't a directory with a `manifest.py`. This is
  available from `publishing-v14`.
- Every publishable entry under `utils/`, and everything publishable in
  `board_configs/desktop/`, is bundled into `pydevices-desktop`, which depends
  on `pydevices`. All artifacts from one release share a version.
- Board `package.json` installers aren't copied into the central MIP index;
  install them from their documented raw GitHub paths.

Adding or removing a publishable entry under `lib/` or `utils/` therefore
changes the next release automatically, so review the generated package set
when you prepare a release. Committed root TOML files such as
`pydevices-desktop.toml` and `gallery.toml` are PyScript filesystem mappings,
not package metadata; their CI validation has to pass before a release.

## The LVGL release

`omnipython-lvgl` carries the binding generator, its three ports and the
`pydevices-lvgl` wheel. Its `release.yml` is the release entry point. It
validates an exact commit SHA or `vX.Y.Z` tag, runs the Linux integration
matrix, and in `release` mode writes the next version to `VERSION` on `main`
and publishes a GitHub Release with an App token, for the reason given above.
That Release starts the ordinary `native-and-wasm` publish for
`pydevices-lvgl`, with no `mip-profile`. Mode `dry-run` runs every gate and
changes nothing.

## The MIP publication queue

Publishing to the MIP index is centralized in `PyDevices/mip` and serialized.
`process-mip-publication-request.yml` runs in the
`pydevices-mip-publication-queue` concurrency group with
`cancel-in-progress: false`, so two releases that both want MIP entries never
race; the second waits.

**Request.** `reusable-request-mip-publication.yml` mints an App token scoped
to `mip` and sends one `repository_dispatch` per profile in the
`mip-profile` input. The MIP leg runs for final releases only: for a
`.devN`, `rcN`, `aN` or `bN` it's skipped, so a pre-release never reaches the
MIP index. A repository whose profile the MIP lockfile doesn't know (the
`palettes` and `pdwidgets` folders of `pydevices`) sets `legacy-index: false`
and sends only the library leg.

**Sync.** The queue consumer, `reusable-synchronize-mip-package.yml`:

1. Checks out `mip` at the `PyDevices` branch tip, not the SHA frozen into the
   dispatch. A dispatch freezes `github.sha` when it's created, so the second
   of two queued publications would otherwise start from a tree that predates
   the first one's lockfile commit and lose its push.
2. Records the release in `pydevices-lock.json`, the source of truth for which
   version of each package is live. Every publishable package needs an entry
   there, added deliberately. The entry's `repository` key is also a guard: a
   dispatch from a different source repository is refused.
3. Re-synchronizes every locked source, not only the one released. `build.py`
   compiles every `manifest.py` in the tree at once, so one package's index
   entry can't be rebuilt in isolation.
4. Removes the temporary `.publication-sources` checkouts, builds the complete
   latest-only index, and verifies that every expected manifest produced an
   entry and that each locked package's index version matches the lockfile.
5. Commits the lockfile with rebase-and-retry: up to three tries of `git push`,
   then `git pull --rebase` on rejection.
6. Assembles and uploads the Pages artifact, which a separate job in the caller
   deploys with `actions/deploy-pages`.

`deploy-mip-index-to-pages.yml` rebuilds the same way on a push to the
`PyDevices` branch or by hand.

## The library index

`PyDevices/lib` serves the library index and is built beside the MIP index, not
from it. Its `publish.yml` takes the same `publish-package-release` dispatch.
A `record` job commits the release's profile and tag to `pins.json` at once and
outside the queue, because GitHub's concurrency group holds one running and one
pending job and a newer pending job replaces an older one, which would lose the
older request's pin. Only the build and the deploy queue, in the
`omnipython-lib-publication-queue` group. Each build rebuilds every package
from the pins with `tools/libbuild.py` from the `pydevices` checkout and
deploys with `actions/deploy-pages`.

A merge to `pydevices` that touches `board_configs/` or `drivers/` sends the
same dispatch with the `boards` profile, so a board or driver is published when
it merges; the next `pydevices` release clears that pin. A profile is refused
when its repository isn't the one `pins.json` names for it. To rebuild without
a release, run `publish.yml` by hand with the inputs empty; to try a library
commit before it's released, give `test-root-ref`, which deploys the build and
records nothing.

## The Release Health dashboard

Every publish run, successful or not, ends with a `report-release-health` job.
It's `continue-on-error`, so a reporting failure never fails the release. It
sends a `repository_dispatch` of type `release-health` to this repository with
the outcome of each stage: TestPyPI, assets, MIP and PyPI. A release headed for
production PyPI reports `pypi` as `pending`, because that upload runs later in
the caller; the caller's `report-pypi` job then sends a partial report that
fills in the outcome on the same row.

`release-health.yml` folds the payload into
[`release-health/data.json`](../../release-health/data.json) and regenerates
[`RELEASE_HEALTH.md`](../../RELEASE_HEALTH.md): one row per distribution,
linked to the run that produced it.
