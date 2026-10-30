# Set up a checkout

Work on this repository from a clone. The scripts and tests need nothing
beyond Python 3 and `ruff`.

```bash
git clone https://github.com/PyDevices/.github.git dotgithub
cd dotgithub
python3 -m unittest discover -s tests -v    # the publishing-script tests
python3 -m pip install ruff
ruff check scripts/ tests/                   # lint, as CI runs it
```

Those two commands are what the `unittest` and `ruff` jobs in
[`checks.yml`](../../.github/workflows/checks.yml) run. The same file lints
every workflow with actionlint, parses each reusable workflow as YAML, checks
that the reusables' `publishing-vN` references agree, and builds the
[main documentation project](../guides/build-and-publish-docs.md) with warnings
as errors, so a pull request here sees all of them.

## Regenerate the org sites

[`data/repos_db.json`](../../data/repos_db.json) is the one source for the
repository map: each repository's tier, description, buttons and the place its
landing page is published. Edit it, never the pages it produces, then run the
generator:

```bash
python3 scripts/generate_sites.py
```

The generator writes into sibling repositories (the portal, the per-repository
`.site/` trees, the organization profile and the `pydevices` ecosystem page),
so clone the repositories it writes to (`PyDevices.github.io`, `pydevices`,
`gallery` and `mip`) side by side, and name this one `dotgithub` on disk, the
folder name the generator looks for:

```bash
git clone https://github.com/PyDevices/.github.git dotgithub
```

A clean run produces no diff; `checks.yml` runs it against fresh clones and
fails on any change.
