# Roll back a release

Pick the registry the bad version reached. In every case the rule is to fix
forward with a new version number rather than rewrite history.

**A bad version on TestPyPI.** Pre-releases are invisible to a default `pip
install`. Yank a final release from the project page: yank, don't delete, so
the history stays honest and installs stop.

**A bad version on production PyPI.** Yank it the same way. The version number
is gone for good: never reuse it.

**A bad publication on the MIP index.** Revert the lockfile commit
(`pydevices-lock.json`) on the `PyDevices` branch of `PyDevices/mip`, then
dispatch `deploy-mip-index-to-pages.yml`. It rebuilds every locked source from
the lockfile at the branch tip and redeploys. Check
`package/<abi>/<name>/latest.json` for the version, and spot-check content too
(the bytes behind one file hash), because GitHub Pages caches for about ten
minutes and the version field alone can mislead.

**A bad GitHub Release.** `gh release edit <tag> --draft` hides it at once and
deletes nothing, so you can decide at leisure.

**A bad `publishing-vN` tag.** It can't change silently: a tag ruleset on this
repository blocks moving or deleting one. The fix is a new `publishing-v(N+1)`
cut with `scripts/cut_publishing_tag.sh`; the old tags stay.

## When the release bot fails

The release automation is a GitHub App. It mints every cross-repository token
(`create-github-app-token`, in the reusable workflows), and a failure names the
missing permission or repository in the log. The organization's owners manage
the App's installation and permissions.

- **A red `Tag release` run** usually means the App lost access to the
  repository. The release can proceed by hand: create the tag and the Release
  with `gh release create` as yourself, and publication starts the same way.
- **A stuck dashboard.** The receiver, `release-health.yml`, runs only on
  `repository_dispatch`, so a stuck dashboard means the App can't reach this
  repository. Rows are additive JSON in `release-health/data.json`; you can
  edit it by hand in a pinch and the next event regenerates the page.
- **A stuck MIP queue.** Runs serialize in the
  `pydevices-mip-publication-queue` concurrency group. Cancel the stuck run,
  then dispatch `process-mip-publication-request.yml` again with the profile,
  repository, ref and version inputs.

For triage when a release fails, see [fix a failed release](fix-a-failed-release.md).
