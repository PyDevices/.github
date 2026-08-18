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
