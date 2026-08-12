# PyDevices transition summary

Status: **Completed**

Session date: 2026-08-11 through 2026-08-12

Scope: PyDevices organization-wide product, packaging, examples, templates,
documentation, and repository identity transition.

## Outcome

The organization is transitioning from a display-oriented development
repository to a driver-oriented, cross-platform Python ecosystem. The
canonical product is now `PyDevices/pydevices`; `PyDevices/pydevices-examples`
is its showcase. Reusable packages originate in the product repository and are
published with names appropriate to each package manager.

The product supports MicroPython, CircuitPython, and CPython, including
desktop, browser/PyScript, Android, Windows, Linux, and Jupyter environments.
The principal portable interfaces are `displaydev` and `audiodev`, supported
by `multimer`, `events`, and `keys`. `eventsys` remains available as an
optional application runtime and event-adapter layer.

## Architecture decisions

### Repository roles

| Repository | Role |
|---|---|
| `pydevices` | Canonical product source: portable libraries, drivers, board configs, tests, and releases |
| `pydevices-examples` | Examples, tutorials, integration documentation, screenshots, and PyScript gallery |
| `pydevices-android-template` | Reusable Android application template |
| `pydevices-pyscript-template` | Reusable installable/offline PyScript PWA template |
| `PyDevices.github.io` | Lightweight organization portal |
| `micropython-lib` | Generated PyDevices MIP mirror and package index |
| `lvgl-bindings` | Canonical LVGL binding generator and shared Python bridge |
| `lvgl-micropython` | MicroPython LVGL integration and builds |
| `lvgl-circuitpython` | CircuitPython LVGL integration and builds |
| `lvgl-python` | CPython, Android, and WebAssembly LVGL wheels |

### Package namespaces

- TestPyPI and future PyPI distributions use the global `pydevices-` prefix,
  except for the root bundle named `pydevices`.
- Python imports remain short: `displaydev`, `audiodev`, `eventsys`,
  `multimer`, `events`, `keys`, and `lvgl`.
- MIP packages remain short and unprefixed because the custom PyDevices index
  already supplies the namespace.
- `pydevices` is the portable bundle. It does not install `eventsys` or choose
  a board by default; pip extras and one selected MIP board package add those
  policies explicitly.

### Board and application boundary

- `board_config.py` remains the selected board's eager UI hardware contract.
- `board_peripherals.py` owns optional or lazy non-UI hardware and exposes
  `PERIPHERALS` plus `load_peripherals()`.
- Board configs never construct `eventsys.Runtime` or any other application
  traffic controller.
- Non-LVGL applications explicitly instantiate `eventsys` when they want it,
  and may provide their own coordinator instead.
- LVGL owns its display, input, timing, refresh, and shutdown bridge through
  `display_driver.py` and does not depend on `eventsys`.

### Gallery and templates

- The PyScript gallery stays with the example source in
  `pydevices-examples`; it is not organization-portal content.
- End-user application starters are separate GitHub template repositories.
- The PyScript template pins a product release and verifies both online and
  service-worker-controlled offline operation.

## Work completed before this summary

### Repository and product identity

- Renamed `micropython-hardware` to `pydevices`.
- Renamed `pydisplay` to `pydevices-examples`.
- Renamed `pydisplay_android` to `pydevices-android-template`.
- Renamed all four LVGL repositories to the `lvgl-*` family.
- Created `pydevices-pyscript-template` and marked both application starters
  as GitHub template repositories.
- Updated local checkout names, Git remotes, workflows, Pages links, badges,
  manifests, recipes, organization navigation, and product cards.

### Product ownership and runtime boundaries

- Moved `eventsys` and its tests into `pydevices/lib/eventsys`.
- Positioned `eventsys` as the optional application runtime/event-adapter
  layer.
- Removed `eventsys` and runtime ownership from all board configs and board
  manifests.
- Added neutral board input/read capabilities and explicit application runtime
  construction.
- Updated non-LVGL examples to opt into the runtime; LVGL examples use the
  LVGL-owned bridge.
- Implemented and characterized the independent LVGL display/input/timer
  bridge. All four `display_driver.py` copies are identical and contain no
  `eventsys` dependency.

### Product layout and board terminology

- Promoted `displaydev` and `audiodev` from driver subdirectories to
  first-class `pydevices/lib/` libraries.
- Kept `board_config.py` and renamed `board_devices.py` to
  `board_peripherals.py` throughout the product, packages, tests, examples,
  templates, and documentation.
- Renamed `DEVICES` to `PERIPHERALS` and `setup_devices()` to
  `load_peripherals()`.
- Added structural tests that enforce the board/application boundary.

### Publishing and distribution

- Moved reusable package publishing authority from the examples repository to
  `pydevices`.
- Added canonical TestPyPI distributions for `displaydev`, `audiodev`,
  `eventsys`, `multimer`, `events`, `keys`, `pydevices-desktop`, and the root
  `pydevices` bundle.
- Applied the `pydevices-*` TestPyPI naming rule to companion packages,
  including `pygraphics`, `palettes`, `pdwidgets`, and LVGL.
- Kept imports and MIP names unprefixed.
- Reset and regenerated the `micropython-lib` fork as an output mirror rather
  than a development source.
- Published coordinated product release `v0.1.0` from `pydevices`.
- Published the live MIP index at
  `https://pydevices.github.io/micropython-lib/mip/PyDevices`.

### Gallery, templates, and organization presence

- Repaired the PyScript gallery generation, manifests, renamed paths, and Pages
  deployment.
- Created a minimal PyScript PWA starter with an app entry point, config,
  loader, manifest, icons, service worker, Pages deployment, and offline smoke
  test.
- Updated the Android template to consume canonical product packages and paths.
- Updated the organization profile, landing site, shared navigation, and
  product-mark assets for the new identities.

### Documentation ownership and naming

- Audited every Markdown file in all 17 organization repositories.
- Moved reusable product architecture, display, event, timer, and application-
  runtime documentation from `pydevices-examples` to the canonical `pydevices`
  product repository.
- Moved the package API overview to `pygraphics` and the shared LVGL callback/
  GC audit to `lvgl-bindings`, their respective source owners.
- Removed obsolete link-only and duplicated package-overview pages from the
  examples repository, then repaired navigation and cross-repository links.
- Standardized first-party narrative documents on lowercase kebab-case,
  including `publishing.md`, `summary.md`, `build-and-flash.md`, and
  `soft-reset-and-bring-up.md`.
- Reserved all-caps Markdown filenames for conventional control/community
  files. Upstream and generated filenames retain their source spelling.
- Recorded this policy in [`repo-layout.md`](repo-layout.md#markdown-naming).

### GitHub repository metadata

- Rewrote the description for every organization repository to match its
  post-transition role.
- Set and live-checked a website for every repository, using the organization
  portal, product documentation, package index, or repository Pages site as
  appropriate.
- Curated 4–10 applicable topics on every repository, exceeding the required
  minimum of two. Template repositories remain marked as templates.

## Verification performed

- Product suite: 316 tests passed with expected platform skips after the final
  contract and layout changes.
- Examples suite: 27 tests passed; generated manifests, 33-demo gallery, and
  48 CircuitPython/MicroPython board pairs audited cleanly.
- LVGL bindings suite: 39 tests passed; all display-driver copies hash-identical.
- Companion suites and package builds passed during their coordinated updates.
- `pydevices` and `pydevices-desktop` source distributions and wheels build and
  pass `twine check`.
- Product Pages and examples documentation builds complete in WSL with temp
  data under `/home/brad/tmp`.
- The PyScript template passes unit, online browser, service-worker reload, and
  offline reload tests.
- `v0.1.0` TestPyPI and MIP publication workflows completed successfully.
- GitHub Pages deployments and renamed repository redirects were verified live.
- A fresh, no-cache TestPyPI install of `pydevices==0.1.0` imported
  `displaydev`, `audiodev`, and `multimer` and confirmed that optional
  `eventsys` was not installed.
- Documentation builds passed for the product, examples, palettes, pdwidgets,
  and pygraphics after the ownership and naming changes. Existing non-strict
  docstring/type-annotation warnings remain outside this transition.
- All CI and Pages workflows triggered by the final repository commits passed.
- Every local checkout is clean, on its intended branch, synchronized with its
  upstream, and all live repository metadata meets the final policy.

## Migration checklist

- [x] Protect and record the baseline.
- [x] Consolidate reusable package ownership in the product repository.
- [x] Move and optionalize `eventsys`.
- [x] Introduce the neutral board contract and remove runtime policy from boards.
- [x] Decouple LVGL from `eventsys` and synchronize all bridge copies.
- [x] Migrate examples and gallery consumers.
- [x] Dry-run wheels, MIP generation, and clean install paths.
- [x] Rename the product, showcase, Android, and LVGL repositories.
- [x] Create the Android and PyScript template repositories.
- [x] Publish coordinated product release `v0.1.0`.
- [x] Complete the organization-wide Markdown ownership/naming audit.
- [x] Normalize descriptions, websites, and topics for every repository.
- [x] Perform the final clean/synchronized repository and live-metadata audit.

## Intentional legacy references

The functioning `pydisplay.readthedocs.io` hostname remains until the external
Read the Docs project slug is changed. Publishing cleanup code may also remove
old `micropython/pydisplay` output trees so stale generated artifacts cannot
survive a release. Neither reference represents current repository or product
ownership.
