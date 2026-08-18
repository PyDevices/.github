# 🤝 Contributing to PyDevices

Thanks for your interest in contributing! PyDevices spans several repos —
this doc covers what's shared across all of them. Each repo's own `README.md`
(and `AGENTS.md`, where present) has project-specific setup, test, and lint
instructions — read that first.

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

Use the issue templates on the relevant repo. Include the runtime
(MicroPython/CircuitPython/CPython), version, and platform/board where
applicable — most bugs here are runtime- or hardware-specific.

For open-ended questions, ideas, or show-and-tell, use
[pydevices Discussions](https://github.com/PyDevices/pydevices/discussions)
instead of opening an issue.

## Pull requests

1. Fork the repo and branch from `main`.
2. Follow that repo's existing code style and test conventions (see its
   `README.md` / `AGENTS.md`).
3. Keep PRs focused — one change per PR is easier to review and revert.
4. Describe *why* the change is needed, not just what changed.

## Regenerating LVGL bindings

If your change touches `lvgl-bindings/binding/`, `lv_conf.h`, or the `lvgl`
submodule, regenerate and commit the affected `generated/*.c` files — see
[lvgl-bindings' README](https://github.com/PyDevices/lvgl-bindings#generate-bindings)
for the exact commands. Don't hand-edit generated files.

## Doc style: emoji

Docs across PyDevices use a small, fixed set of emoji as landmarks on
section headings — not decoration. Each emoji has exactly one meaning and is
only used on a heading that's actually about that thing:

| Emoji | Meaning | Use on headings like |
|---|---|---|
| 🚀 | Getting started / install / build | "Quick start", "Installation", "Build", "Setup" |
| 🎨 | Examples / demos | "Examples", "App starter", a demo's own title |
| 💬 | Getting help / support | "Get help", "Getting help", "Still stuck?" |
| 🐛 | Reporting bugs / issues | "Reporting bugs", "Reporting bugs / requesting features" |
| 🤝 | Contributing | "Contributing" (as a heading or doc title) |
| 📚 | Documentation / reference links | "Documentation map", "Quick links" |
| ⚠️ | Troubleshooting / things that can go wrong | "Troubleshooting" (doc title), a warning callout |

Rules of thumb:

- Only use these seven — don't add a new one-off emoji to "break up the
  monotony." If a heading doesn't match one of these meanings, leave it
  plain.
- One emoji per heading, and only on headings, not scattered through body
  text (an inline `⚠️ **Note:**` callout is the one exception).
- Skip a doc/repo entirely if it doesn't have a heading that genuinely
  matches — don't invent a "Getting started" section just to have somewhere
  to put 🚀.
- If several headings in the same doc are parallel alternatives for the
  same category (e.g. "Build (Make ports)" *and* "Build (CMake ports)"),
  tag none of them rather than picking one arbitrarily — repeating the same
  emoji on adjacent headings reads as noise, not a landmark.
