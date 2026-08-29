# Operations runbook

Companion to [publishing-automation.md](publishing-automation.md) (the
release runbook). This file covers what to do when things go wrong, and
how new maintainers and agents come aboard.

## Rollback

Exercised twice in production during the modernization program; the
patterns are proven.

**A bad version reached TestPyPI**: pre-releases are invisible to default
pip; final releases can be yanked from the project page (yank, don't
delete — it preserves honest history and stops installs). Production
PyPI: same, plus the version number is burned forever — never reuse it.

**A bad publication reached the MIP index**: revert the lockfile commit
in PyDevices/mip, then dispatch `deploy-mip-index-to-pages.yml` (it
rebuilds every locked source from the branch-tip lockfile and redeploys).
Verify: `package/<abi>/<name>/latest.json` version AND a content spot
check (a file hash's bytes), not just the version field — Pages caches
for ~10 minutes.

**A bad GitHub Release**: `gh release edit <tag> --draft` hides it
immediately without deleting anything; decide at leisure. (This rescued
the ViperIDE mis-release.)

**A bad publishing-vN tag**: cannot happen silently — the tag ruleset on
this repo blocks moves and deletions. The fix is always a v(N+1); v3–v6
history stays.

## Incident triage

1. `workflow_attention.sh` at the workspace root: current failures and
   active runs, org-wide.
2. `RELEASE_HEALTH.md` in this repo: last publish outcome per
   distribution, updated by every publish run, pass or fail.
3. A red `Tag release` run usually means the App lost repo access or
   permissions (installation settings) — the release can always proceed
   manually (tag + `gh release create` as a human; publication triggers
   identically).
4. A "second publication lost" or "index went backwards" event is the
   frozen-SHA class: both known holes are fixed (branch-tip checkouts +
   rebase-retry), so a recurrence means a NEW instance of the class —
   look for a checkout without an explicit `ref:` in whatever workflow
   wrote last.

## Bot-failure recovery

- The release-automation App mints all cross-repo tokens
  (create-github-app-token in the reusables). Failures name the missing
  permission or repo in the log. Brad owns the App's installation and
  permissions; agents never hold its key (roadmap rule 3).
- The dashboard receiver (`release-health.yml`) is repository_dispatch
  only; a stuck dashboard means the App can't reach this repo. Rows are
  additive JSON in `release-health/data.json` — safe to hand-edit in a
  pinch, the renderer regenerates the page on the next event.
- MIP queue stuck: runs serialize in the
  `pydevices-mip-publication-queue` concurrency group; cancel the stuck
  run, re-dispatch `process-mip-publication-request.yml` with the
  profile/repo/ref/version inputs (all profiles are in the choice list).

## Onboarding

- **A human maintainer**: CONTRIBUTING.md here, then the repo they'll
  touch (every repo states its role, status, and build path in its
  README), then publishing-automation.md before their first release.
- **An agent**: the private workspace anchor repo holds the agent
  contract (`docs/agent-contract.md`), the knowledge modules
  (`docs/agent-knowledge/`), and the fleet definitions
  (`.claude/agents/`). New agents are forged through `/forge-agent` and
  are not trusted until their smoke task has run green.
