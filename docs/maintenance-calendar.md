# Recurring maintenance calendar

## Continuous (automated)
- Release Health dashboard: every publish run reports, pass or fail.
- cmods mirror-drift + shellcheck: every push to cmods.
- dotgithub self-checks (actionlint, YAML, generator idempotency, ruff):
  every push/PR here.
- Per-repo publish/test CI: every push per repo.

## Weekly (automated, Mondays)
- lvgl-bindings font drift (06:17 UTC) — regenerates fonts/*.bin, fails
  on divergence.
- micropython-pydevices overlay compatibility (06:43 UTC) — every
  profile applies clean to the pinned upstream.

## Monthly (manual, ~first weekend)
- Merge the month's dependabot PRs (they arrive grouped; batch-merge is
  routine).
- Skim TestPyPI project pages for anything unexpected.
- Check upstream MicroPython releases: a new stable is INFORMATION, not
  an obligation — moving any pin (upstream v1.28.0, lvgl submodule,
  PyScript, CircuitPython oracle) is deliberate work with its own
  verification, never routine.

## Quarterly (scheduled → issue)
- The standing cold-eyes review: `cold-eyes-review.yml` opens an issue
  here each quarter naming a rotating sample of repositories and the
  scenarios to re-run (S1 clean build, S4 stranger's first try, S5
  release health, S6 the org walk). The bar decays without enforcement;
  this is the enforcement.
- CircuitPython oracle stance review: 10.2.1 stays pinned until moving
  it is chartered as its own re-port (audioif's call, not routine).
