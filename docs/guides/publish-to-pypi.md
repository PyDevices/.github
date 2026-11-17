# Publish to PyPI

PyPI is where every release goes. Set `pypi-publish: true` on the package's
publish call, and every version of that package goes there, pre-releases
(`.devN`, `aN`, `bN`, `rcN`) included. pip installs a pre-release only when
asked with `--pre` or an exact version, so a development release doesn't reach
a plain `pip install`. Every repository that publishes sets it.

Three things turn it on for a package, and missing one makes the run fail at
the PyPI end or skip the upload, never publish somewhere unintended:

1. The `pypi-publish: true` input on the call to
   `reusable-publish-release-packages.yml`.
2. Two jobs in the package's own publish workflow, shown below.
3. A matching Trusted Publisher on the PyPI project: owner `PyDevices`, the
   repository, the workflow file that holds the `pypi` job (usually
   `publish-release-packages.yml`), environment `pypi`. A repository that
   builds several distributions in one run needs a publisher on each
   project.

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
output to `true` for a release whose build succeeded, and the caller
uploads.

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

The `pypi` job runs in the repository's `pypi` GitHub Environment, which has
no required reviewer, so a release reaches PyPI as soon as its checks pass,
and limits deployments to `v*` tags. Check it with
`gh api repos/PyDevices/<repository>/environments/pypi`. `report-pypi` fills in
the PyPI outcome on the release's Release Health row, which shows `pending`
until it runs.

Because the environment accepts only `v*` tags, a `workflow_dispatch` retry
from `main` can't reach it. A retry that needs PyPI dispatches on the tag, and
so runs the caller file as it was at that tag.
