# Cut your first release

You release a package by merging a pull request. Pick a repository that
publishes (see [what each repository publishes](../reference/release-workflows.md#what-each-repository-publishes))
and start with a development version. It reaches TestPyPI, the release's
attached files and, for a repository that requests it, the library index, but not the MIP index or production PyPI.

```bash
gh workflow run prepare-release.yml --repo PyDevices/<repository> -f version=X.Y.Z.dev1
```

Within a minute the repository has a pull request named `Release X.Y.Z.dev1`
on a `release/vX.Y.Z.dev1` branch. It changes `VERSION` and adds a section to
`CHANGELOG.md`. Check the version, read the changelog section, wait for CI,
then merge it.

Merging tags `vX.Y.Z.dev1`, creates the GitHub Release, and starts the
publish run. When the run finishes, the package is on TestPyPI and the
release's row in [`RELEASE_HEALTH.md`](../../RELEASE_HEALTH.md) shows each
stage's outcome with a link to the run.

The [release guide](../guides/release-a-package.md) covers a final release,
a retry and the manual fallback, and
[the release chain](../how-it-works/release-chain.md) explains why each step
exists.
