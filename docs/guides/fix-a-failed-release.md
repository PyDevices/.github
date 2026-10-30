# Fix a release that failed

Start with two places. `RELEASE_HEALTH.md` at the root of this repository
shows the last publish outcome for each distribution, updated by every publish
run, pass or fail, with a link to the run. The run's own log names the failing
job.

Two situations are worth recognising before you read the table:

- **A second publication lost, or the index went backwards.** Both known
  causes are fixed (the queue checks out the branch tip, and the lockfile
  commit retries after a rebase). A recurrence means a new instance of the same
  kind: look for a workflow step that checks out without an explicit `ref:`.
- **A package moved repositories.** The MIP lockfile names the repository each
  profile may be published from, and refuses a dispatch from another. The
  releasing repository's `request-mip-publication` job reports success; only
  `mip`'s own run goes red. Tag in the new repository, then change `repository`
  and `ref` for the profile in `pydevices-lock.json` on `mip`'s `PyDevices`
  branch, then rerun the failed `mip` runs.

| Symptom | Meaning and response |
|---|---|
| No publication run after pushing a tag | A tag alone isn't the trigger. Publish the GitHub Release. |
| `VERSION contains ... but the release tag is ...` | Fix and commit `VERSION`, then make a new tag and version with a fresh "Prepare release" run. Don't move a published tag. |
| TestPyPI `invalid-publisher` | The job tried OIDC Trusted Publishing without a matching publisher. TestPyPI uses `__token__` and `TESTPYPI_API_TOKEN`. |
| TestPyPI authentication failure | Check that `TESTPYPI_API_TOKEN` exists for that repository, has permission for the project, and hasn't expired or been revoked. |
| TestPyPI duplicate-file response | Retry with a current coordinator, which sets `skip-existing: true`; otherwise publish a new version. |
| Production PyPI upload didn't run | Check four things: `pypi-publish: true` on the caller, the caller's own `pypi` job ([production PyPI](publish-to-pypi.md)), a final version (not `.devN` or `{a,b,rc}N`), and the `pypi` environment's reviewers approving the run. |
| PyPI `invalid-publisher` naming `PyDevices/.github` in `job_workflow_ref` | The upload ran inside the reusable workflow, which PyPI can't match. Move it to the caller's `pypi` job on a publishing tag that has `pypi-gate`. |
| A MIP request is queued | Expected: one concurrency group processes publication requests in order. |
| MIP validation sees `.publication-sources/manifest.py` | The shared sync job didn't remove its temporary checkouts. Start a fresh run on a current `publishing-v*` tag. |
| Pages setup or an action download returns 429, 503 or 504 | Usually transient. Retry the failed MIP job and check the live index afterwards. |
| The source workflow passed but MIP is still old | Look at the matching run in `PyDevices/mip` and wait for Pages to deploy. Success in the source repository only confirms the dispatch. |
| A native wheel platform is missing | Fix the wheel matrix and publish a new version. TestPyPI can't take a replacement for an existing filename. |
| `RELEASE_HEALTH.md` shows a stale row | The reporting job is `continue-on-error`, so a real failure elsewhere doesn't block it, but an outage of this repository or a missing App installation would. Open the linked run. |

To retry or correct a release, see [release a package](release-a-package.md).
To pull a version back, see [roll back a release](roll-back-a-release.md).
