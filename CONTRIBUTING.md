# 🤝 Contributing to PyDevices

Thanks for your interest in contributing! PyDevices spans several repos —
this doc covers what's shared across all of them. Each repo's own `README.md`
(and `AGENTS.md`, where present) has project-specific setup, test, and lint
instructions — read that first.

## Design principles

Org-wide standards every shipped design is measured against — starting
with completeness ("any pairing the protocols permit that the design does
not deliver is a defect in the design, not a feature request") — live in
[`docs/design-principles.md`](docs/design-principles.md).

## Where things live

Repo directory and root-file layout (`src/`, `lib/`, `tests/`,
`requirements-dev.txt`, …): see [`docs/repo-layout.md`](docs/repo-layout.md).

The full repository map — every repo, grouped by tier, with what each one owns —
is generated from `data/repos_db.json` and published at
[pydevices/docs/ecosystem.md](https://github.com/PyDevices/pydevices/blob/main/docs/ecosystem.md) and on the
[org profile](https://github.com/PyDevices). Do not restate it here; it drifts.

If you're not sure which repo an issue or PR belongs to, open it on
[pydevices](https://github.com/PyDevices/pydevices/issues) — we'll help route it.

## 🐛 Reporting bugs / requesting features

Use the issue templates on the relevant repo. Include the interpreter
(MicroPython/CircuitPython/CPython), version, and platform/board where
applicable — most bugs here are interpreter- or hardware-specific.

For open-ended questions, ideas, or show-and-tell, use
[pydevices Discussions](https://github.com/PyDevices/pydevices/discussions)
instead of opening an issue.

## Pull requests

1. Fork the repo and branch from `main`.
2. Follow that repo's existing code style and test conventions (see its
   `README.md` / `AGENTS.md`).
3. Keep PRs focused — one change per PR is easier to review and revert.
4. Describe *why* the change is needed, not just what changed.

## Generated files and sync targets

Some repositories are the **single writer** of files that other
repositories carry as **sync targets**: a generator produces them, and a
sync script in each consumer overwrites its copies with whatever the
generator last produced. A hand edit to a synced file in a consumer is not
preserved — the next sync overwrites it. Each repository's `README.md` /
`AGENTS.md` says which of its files are generated, where they come from,
and how to regenerate them. Make the change in the generator and
regenerate; don't hand-edit generated files anywhere else.

## Doc style: emoji

Docs across PyDevices use a small, fixed set of emoji as landmarks on
section headings — see [`docs/doc-style.md`](docs/doc-style.md) for the
full table and rules of thumb before adding or changing heading emoji.
