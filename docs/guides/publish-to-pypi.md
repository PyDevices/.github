# Publish to production PyPI

Every release reaches TestPyPI. Production PyPI is a decision you make per
package: set `pypi-publish: true` on the package's publish call. The only
repository that sets it today is `audiodsp`.

Three things turn it on for a package, and missing one makes the run fail at
the PyPI end or skip the upload, never publish somewhere unintended:

1. The `pypi-publish: true` input on the call to
   `reusable-publish-release-packages.yml`.
2. Two jobs in the package's own `publish-release-packages.yml`, shown below.
3. A matching Trusted Publisher on the PyPI project: owner `PyDevices`, the
   repository, workflow `publish-release-packages.yml`, environment `pypi`.

## Why the upload is in the caller

PyPI matches a Trusted Publisher against the workflow that runs the upload
job. Inside a reusable workflow that is
`PyDevices/.github/.github/workflows/reusable-publish-release-packages.yml` at
a publishing tag, which no repository's publisher can name, so an upload from
there fails with `invalid-publisher` (see
[pypa/gh-action-pypi-publish#166](https://github.com/pypa/gh-action-pypi-publish/issues/166)
and [PyPI's note on reusable
workflows](https://docs.pypi.org/trusted-publishers/troubleshooting/#reusable-workflows-on-github)).
So the reusable's `pypi-gate` job only decides: it sets the `pypi-publish`
output to `true` for a final release whose build and TestPyPI upload
succeeded, and the caller uploads.

## The two caller jobs

```yaml
  pypi:
    needs: publish
    if: >-
      !cancelled() && needs.publish.outputs.pypi-publish == 'true'
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v8
        with:
          name: ${{ needs.publish.outputs.dist-artifact }}
          path: dist
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          skip-existing: true

  report-pypi:
    needs: [publish, pypi]
    if: >-
      !cancelled() && needs.publish.outputs.pypi-publish == 'true'
    uses: PyDevices/.github/.github/workflows/reusable-report-pypi-result.yml@publishing-vN
    with:
      distribution-name: <distribution>
      version: ${{ needs.publish.outputs.version }}
      pypi-result: ${{ needs.pypi.result }}
    secrets: inherit
```

The `pypi` job runs in the repository's `pypi` GitHub Environment, which
needs a required reviewer and deployments limited to `v*` tags. Check it with
`gh api repos/PyDevices/<repository>/environments/pypi`. `report-pypi` fills in
the PyPI outcome on the release's Release Health row, which shows `pending`
until it runs.

Because the environment accepts only `v*` tags, a `workflow_dispatch` retry
from `main` can't reach it. A retry that needs PyPI dispatches on the tag, and
so runs the caller file as it was at that tag.

TestPyPI is unaffected: it authenticates with the `TESTPYPI_API_TOKEN` secret,
not Trusted Publishing, and its upload stays in the reusable workflow.
