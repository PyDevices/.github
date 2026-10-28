# AGENTS.md

- Tests: `python3 -m unittest discover -s tests -v` from the repo root. Lint is `ruff check scripts/ tests/`.
- `publishing-vN` tags are immutable: a bad one is fixed with a new `vN+1`, never by moving or deleting the tag. The reusable workflows are called by that tag, not a branch ([publishing automation](docs/publishing-automation.md), [operations runbook](docs/operations-runbook.md)).
- Don't hand-edit `RELEASE_HEALTH.md` or `release-health/data.json`; the release-health workflow rewrites them on every release report.
- Edit `data/repos_db.json`, never the generated markup, then run `python3 scripts/generate_sites.py`. It writes into the sibling repositories (`profile/README.md`, per-repo `.site/` trees, the pydevices ecosystem page), so run it with the repos checked out side by side ([README](README.md)).
- `.cursor/environment.json` lists the repos Cursor's cloud environment clones; keep it in step by hand when a public repository is added or retired.
- Repository layout and file-naming conventions, including the `MICROPYPATH` / `PYTHONPATH` search paths: [repo-layout](docs/repo-layout.md). Doc and docstring style: [doc-style](docs/doc-style.md), [docstrings](docs/docstrings.md).
- Other repositories' generated files are overwritten by their sync scripts, so change the generator, not the copy ([CONTRIBUTING.md](CONTRIBUTING.md#generated-files-and-sync-targets)).
