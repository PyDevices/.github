# Doc style: emoji

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

## Where this applies (amended 2026-08-29, Gate 4 decision)

Practice across the organization settled differently from this document's
original ambition, and the convention below now describes what is real
rather than what was hoped:

- **READMEs are emoji-free.** A README renders on GitHub first, where
  restraint reads better. This is the prescribed convention (a handful of
  READMEs still carry stray emoji; Phase 4 removes them as each repo gets
  its pass).
- **Docs-site pages** (mkdocs/portal pages) may use the landmark set
  above, sparingly, on headings only — the original rules (one per
  heading, only the fixed set, never in body text or code) apply there.
- A repo using none at all is compliant. The failure mode this document
  guards against is *decorative scatter* — emoji in body text, list
  items, or invented one-offs — not absence.
