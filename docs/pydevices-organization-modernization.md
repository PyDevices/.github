# PyDevices Organization Modernization — Agent Execution Contract and Roadmap

**Status:** EXECUTING. Brad gave GO on 2026-08-28 with every hard start
condition met (audio program finished and audited; micropython-vst3
published and merged; lvgl generator overhaul finished, audited, and
released as lvgl-bindings v9.5.15 / lvgl-python v9.5.38).

**Owner:** Brad / PyDevices

**Canonical workspace:** /home/brad/gh/pydevices

**Revision:** 2026-08-27, amended the same day for cloud execution (section
2.1). This file supersedes the 2026-08-26 draft in full and is self-contained.
No amendment files exist; any reference to "Amendment A" or "Amendment C" is
stale and must be ignored.

## 1. Mission — the bar

The goal of this program is that an expert maintainer inspecting any PyDevices
repository cold — or the organization as a whole — finds no evidence of
neglect and no dependence on Brad's private environment, and concludes they
could not have done it materially better.

That bar has two lenses, and every phase must satisfy both:

- **The rigor lens** (think: a MicroPython core developer). Reads the code,
  the build glue, the patch queue, and the git log before the README. Values
  clean-clone builds, minimal and purposeful diffs, disciplined commit
  messages, and downstream patches maintained the way a Linux distribution
  maintains them: versioned, attributed, tested, individually justified.
- **The user lens** (think: an Adafruit maintainer). Opens the README first,
  then tries the quickstart. Values first-try success, examples that actually
  run, consistent patterns across repositories so learning one teaches all of
  them, predictable releases, and an organization that feels like one product.

The operational standard is **deliberate everywhere**: not flawless — no
organization is — but nothing a visitor touches shows accident or neglect.
Every rough edge is a labeled decision. Anything that works only in Brad's
workspace is a defect by definition.

The end state, in priority order:

1. **Releases are boring.** One reviewed pull request produces the tag, the
   GitHub Release with assets, the package publication, and the downstream
   updates — verified by an always-current health dashboard.
2. **Every supported public build stands alone.** A user builds a component
   from its own repository, upstream MicroPython/CircuitPython, and declared
   dependencies. cmods is Brad's convenience, never a prerequisite.
3. **Downstream runtime changes have a real home.** Patches and variants live
   in a versioned, tested overlay with provenance — credibility that does not
   depend on upstream pull requests.
4. **A stranger succeeds.** README to working example on a supported target,
   first try, for every active repository.
5. **The organization runs hands-off between decisions.** Bots prepare, verify,
   and report; Brad reviews and merges. Nothing publishes itself beyond
   explicitly approved policy.
6. Optionally, a **central cockpit** (Codespaces/devcontainer) for Brad and
   attached agents — a convenience surface, never a hidden requirement.

Explicit non-goals: no rename or rebrand (names are frozen for this program);
no long-lived MicroPython fork; upstream pull requests are possible outcomes,
never prerequisites.

## 2. Hard start condition

Execution is a cloud handoff: the executing agent runs in Claude cloud
sessions (section 2.1), not on Brad's workstation. The agent must not change
repositories, GitHub settings, package registries, or other external state
until all of the following hold:

1. The in-flight instrument-library program on `audioif` and
   `micropython-vst3` (rule 9) is completely finished, `micropython-vst3`
   (currently the only workspace repository with no GitHub remote, verified
   2026-08-27) has been published, and both repositories' remotes are in sync
   with Brad's local checkouts.
2. The pre-handoff checklist (section 2.2) is complete.
3. Brad gives the exact instruction:

       GO

Before GO, the agent may read this roadmap, read the pushed repositories, and
answer questions, but must not begin discovery probes or implementation.

### 2.1 Execution environment

**Amended at GO (2026-08-28, per Brad):** the executor is a local Claude
session on Brad's workstation, working in the canonical workspace — not a
cloud session. The cloud-handoff design below is retained as an optional
future mode; where it says "cloud session", read "executing session". The
proof surface, checkpoint-packet, and gate rules are unchanged, except
that on-hardware and workstation-only verification no longer needs a
separate session.

- The original design: a Claude cloud session authenticated through the Claude
  GitHub app, installed org-wide with all-repository access (verified
  2026-08-27) — covering the private `workspace` anchor repository; the rest
  of the organization is public.
- The session anchor is the private `workspace` repository: a session starts
  there and runs its `bootstrap.sh`, which delegates to the public manifest
  (`workspace/repos.json` + `workspace/bootstrap.sh` in the `.github`
  repository) to clone or fetch every active repository into the anchor
  checkout, git-ignored there. The anchor also holds private program
  documents (gate packets, audit findings, in its `docs/`) and maintainer
  tooling — and, by its boundary rule, never anything a public build needs.
  Every session begins by bootstrapping and reading this roadmap.
- The cloud sees only what is pushed. Local working trees, uncommitted
  changes, and workstation state are invisible; anything the program needs
  must reach a remote first.
- The proof surface is CI. GitHub Actions runs (including Windows runners)
  are the clean-environment evidence for the scenarios; the browser simulator
  may run headless in-session. On-hardware verification is owned by Brad or
  an explicitly requested workstation session and is recorded as such
  (scenario S4).
- Work proceeds session by session: checkpoint packets land as PR
  descriptions, issues, or the anchor repository's private `docs/`; gates map
  to session boundaries; nothing may depend on memory that is not in a
  repository.

### 2.2 Pre-handoff checklist (workstation)

Completed from the workstation before the handoff; the cloud agent verifies
rather than performs these:

1. Capture the uncommitted Adafruit_MP3 Windows patch — **done 2026-08-27**:
   `cmods/patches/adafruit_mp3/0001-windows-msvc-inline-assembly.patch`.
2. Push every in-scope repository so remotes match local. (`audioif` and
   `micropython-vst3` sync is owned by the in-flight program's completion,
   condition 1 above.)
3. Grant the Claude GitHub app access to the in-scope repositories.
4. Rebuild and commit the distributed interpreter binaries (`pydevices/bin`,
   the site and workbench wasm) from merged, pushed sources only — never from
   an unmerged branch.

## 3. Authority and safety rules

1. Treat this roadmap as the controlling plan. If a material architectural
   change emerges, update this file in a reviewable change and obtain approval
   before continuing.
2. Inspect before changing anything.
3. Never expose, print, copy, or commit secrets. In particular, never read,
   move, or upload the `pydevices-release-automation` GitHub App private key;
   Brad installs credentials himself.
4. Never rewrite public history.
5. Never delete a repository, release, package, tag, branch, or user asset
   without specific approval for that exact destructive action.
6. Never rename or transfer a repository or organization.
7. Never publish to production PyPI or another production registry without a
   separate explicit approval naming the package.
8. Keep changes reviewable and rollbackable. Default to at most five
   repositories per approval batch.
9. Preserve user work and unrelated local changes. **In-flight work outranks
   this program**: repositories with an active plan or feature branch (at
   revision time: `audioif` on `instrument-library-tier`, `micropython-vst3`
   on `instrument-library-cutover`, per the audioif instrument-library
   refactor) must not be modified without checking with Brad first.
10. Prefer reversible changes: draft PRs, dry runs, previews, TestPyPI.
11. Use least-privilege credentials and pinned GitHub Action revisions.
12. Do not broaden scope because a convenient adjacent change is available.
13. Do not create or name a new repository (including the runtime overlay)
    until Brad approves its ownership boundary and name.
14. Stop at every gate. Approval at one gate does not imply approval at the
    next. Continue only on the exact phrase `APPROVE GATE n`.
15. Deliberate exceptions (section 4.2) are design decisions, not defects. Do
    not "fix" them; record them in the exceptions ledger and design around
    them.

## 4. What is already known

A prior audit (2026-08-26) and working history have already established the
baseline below. The agent must **spot-check these cheaply, not re-derive
them**. Anything that fails a spot-check is a finding; everything else is
carried forward as fact.

### 4.1 Defects to fix

1. **Workflow drift**: most publishing repositories call `publishing-v3`;
   `audioif` and newer shared logic use `publishing-v4`. Consolidate on a new
   immutable `publishing-v5` contract; leave existing v3/v4 tags untouched.
2. **workbench release contract broken**: its release workflow fires only on
   `mcp-v*` tags, but the repo carries `v0.6.x` tags — tags exist with no
   GitHub Releases.
3. **lvgl release race**: `lvgl-bindings` propagates helpers/bindings to
   `lvgl-python` / `lvgl-micropython` / `lvgl-circuitpython` via a trigger
   workflow; a parallel manual PR caused a non-fast-forward race and a
   silently skipped release (2026-08-21). The sync must be serialized and the
   single-writer rule (edit only in `lvgl-bindings`) enforced by convention
   and documentation.
4. **No branch protection or rulesets** on the publishing repositories.
5. **Production PyPI names unregistered.** All eight distributions exist only
   on TestPyPI; the production names were free when checked. This is a
   name-squatting exposure and the most urgent external action in the program
   (Gate 1 decision).
6. **Releases ship no assets** (six of the seven repositories with GitHub
   Releases attach none).
7. **Retired PyDevices URLs 404** in search results. Add redirects; this is
   also the standing argument for the name freeze.
8. **audioif resolves dependencies by sibling path** (ulab, Adafruit_MP3).
   The Windows compatibility patch to Adafruit_MP3 (`assembly.h`) was captured
   pre-handoff to `cmods/patches/adafruit_mp3/` (checklist 2.2); in Phase 2
   its ownership moves to the native pilot's patch queue.
9. **Runtime patches and variants live only in cmods**: MicroPython Windows
   networking/SSL/select mailbox patches applied by `build_mp.sh`, Windows FFI,
   WebAssembly port additions and the external wasm `variants` directory,
   wasmbridge, fetch-backed requests, wasm locking. No public home, no
   versioned application process.
10. **The CircuitPython oracle pin is not a mechanism**: `cmods/circuitpython`
    is a detached HEAD at tag 10.2.1 declared in no repository; a fresh clone
    could land elsewhere and silently invalidate every parity golden. Declare
    the pin in a checked-in location with a status warning. (Do not *move* the
    pin — see section 4.2.)
11. **Generated artifacts without drift checks**: `lvgl-bindings/fonts/*.bin`
    are committed outputs no CI regenerates; a moved lvgl pin silently
    diverges them. The generated-code contract (section 6, scenario S2 family)
    must cover this class.
12. **Interpreter binaries tracked in git**: `pydevices/bin` carries ~34 MB of
    rebuilt interpreter binaries with `core.fileMode false`, producing the
    recurring lost-execute-bit failure class (rc=126). Propose moving binary
    distribution to release assets with a fetch script; Brad decides.
13. **Stale TestPyPI leaf packages** (`pydevices-multimer`, `-displaydev`,
    `-events`, `-keys` at 0.1.3) look like broken releases to a stranger.
    They are retired (section 4.2); label or clean up so the *appearance*
    matches the decision.

### 4.2 Deliberate exceptions (the exceptions ledger, seeded)

These are decisions, not drift. The Definition of Done (section 9) is
satisfied *with* them in place, provided each is recorded and visible where a
stranger would otherwise misread it.

- **Versions are chosen by a human.** Nothing computes the next version.
  Release automation must preserve this: the release PR is where the human
  reads, edits, and approves the version before merging.
- **Only `pydevices`, `pydevices-desktop`, `pygraphics`, `palettes`, and
  `pdwidgets` publish.** The pydevices leaf distributions are retired.
- **lvgl-python is a sync target.** Helpers are edited only in
  `lvgl-bindings`; the trigger workflow owns propagation; a manual merge
  suppresses the release by design. Only `lvgl-python` publishes.
- **The CircuitPython oracle stays pinned at 10.2.1** while audioif parity
  work is live. Moving it is a re-port and its own future phase, owned by the
  audioif plan, not this program.
- **micropython-vst3 is remoteless on purpose** until Brad publishes it (its
  lint runs as a ctest for exactly that reason). Publication is the GO
  precondition, not this program's job.

Additions to this ledger require Brad's approval and must state what a
stranger will see and where the decision is documented.

## 5. Operating principles

### 5.1 Releases first

The original priority stands: the highest-value move is making releases boring
and dependable. Release automation is Phase 1, not a reward at the end.
It is also what makes every later phase cheap to verify — each subsequent
change rides an automated, observable release path instead of a manual one.

### 5.2 The dependency direction

    Target:   cmods ──▶ component's public build contract ──▶ MicroPython
                                    └── declared, pinned dependencies

    Standalone user:  MicroPython + component repo + declared dependencies

cmods may aggregate, pin known-good portfolios, cache toolchains, and compose
advanced profiles — as a *consumer* of public contracts. No supported public
build may require knowledge or files that exist only in cmods. MicroPython's
external C module mechanism (`micropython.mk`, `micropython.cmake`, manifests)
makes this achievable without upstream changes.

### 5.3 The patch queue is the credibility

A meticulously maintained downstream patch queue — mailbox format, provenance,
compatible-version range, ordered series, a test per patch, scheduled
application checks against upstream — is rarer and more persuasive to the
rigor lens than upstream PRs. Upstreaming becomes an explicit per-patch
decision made from strength. (audioif has already found and fixed real
upstream bugs — the synthio oscillator wrap, the Mixer reset, the biquad
peaking sign — documented in its `docs/upstream-diff.md`; reporting those
upstream proceeds on the audioif plan's own schedule.)

### 5.4 Automation reduces maintenance, not conceals it

Bots prepare changes, validate releases, merge narrowly defined low-risk
updates, and keep a health dashboard current. They never silently publish,
never make architectural decisions, and never paper over a broken contract.

### 5.5 Taste over compliance

Checklists reach "nothing is broken"; the bar in section 1 is reached by
evidence of care. When a rule in this document fights clarity or quality in a
specific case, the agent proposes the deviation at the next checkpoint instead
of complying badly or deviating silently.

### 5.6 Portfolio, not showcase

Roughly twenty repositories need attention. audioif and the runtime patches
are *evidence* of portfolio-wide problems, not the center of the program. The
pilot set is chosen at Gate 1 for archetype coverage; audioif may be in it on
merit, but nothing is designed around any single repository.

## 6. Inspection scenarios

Scenarios are the currency of this program: each gate is defined by named
scenarios passing with recorded evidence (exact commands, transcripts, links),
not by checklist completion. A scenario passes only from a clean environment
with no cmods present unless the scenario says otherwise.

- **S1 — The cold build** (rigor): On a clean machine, using only a
  component repository's documentation, clone it plus upstream
  MicroPython/CircuitPython plus its declared dependencies; build the
  documented profile; run its tests. Missing dependencies fail early with a
  useful message. Evidence from a GitHub Actions run on a clean runner
  (Linux or Windows) satisfies the clean-machine requirement.
- **S2 — The patch reader** (rigor): Open the patch queue cold. Every patch
  states purpose, provenance, upstream-version range, and order; the series
  applies cleanly to the pinned upstream; each patch's effect is demonstrated
  by a test; scheduled CI proves the series against supported upstream
  versions and fails loudly when it stops applying. Generated committed
  artifacts (bindings, font bins) have drift checks in the same spirit.
- **S3 — The log reader** (rigor): `git log` from program start onward reads
  as disciplined: scoped, single-purpose commits with honest messages.
  History before the program is what it is (rule 4); the line where the log
  becomes disciplined is itself the statement.
- **S4 — The quickstart** (user): A stranger with a supported target follows
  the README from the top and reaches a working example on the first try.
  Examples are exercised in CI where feasible (the browser simulator makes
  this practical for display-oriented repos).
- **S5 — The boring release** (operations): A release is: review one
  generated PR (human edits/approves the version — section 4.2), merge.
  Tag, GitHub Release with assets, package publication, MIP lock bump, and
  docs follow automatically; the Release Health dashboard turns green or
  says exactly what failed. No unwatched manual steps.
- **S6 — The org walk** (both): From the organization landing page into any
  repository: accurate description, topics, status label, license, support
  boundary, live links, no retired-URL 404s, and nothing that *looks*
  abandoned without saying so.
- **S7 — The absent maintainer**: For thirty days Brad only reviews and
  merges. Dependency updates keep flowing, health stays visible, nothing
  publishes beyond approved policy, and the runbooks are sufficient for an
  agent to triage a failure without improvisation.

## 7. Execution phases and approval gates

### Phase 0 — Verify and complete the picture (time-boxed: days, not weeks)

After GO:

1. Bootstrap the workspace from the manifest (section 2.1); report anything
   the manifest missed as a finding, and extend it as the inventory
   completes.
2. Spot-check every section 4.1 finding; record deltas. Verify the
   pre-handoff checklist (section 2.2) actually holds.
3. Complete the inventory: every local and GitHub repository including the
   newly published one(s) — role, audience, archetype, lifecycle, release
   path, dependency set, cmods assumptions. Focus effort on what is *unknown*;
   do not re-derive section 4.
4. Map every publisher's exact release path end to end (VERSION file, tag
   match enforcement, TestPyPI, MIP lock bump).
5. Propose: the Phase 1 release pilot (default: `palettes`, the lowest-risk
   pure-Python publisher); the Phase 2 native pilot; the runtime overlay
   boundary and name (provisionally `micropython-pydevices`); the production
   PyPI registration list; the workbench tag policy.

#### Gate 1 — Baseline and pilot approval

Present: inventory and delta report; archetype/lifecycle table; release-path
map; pilot proposals; overlay proposal; and at most five decisions, which
must include **production PyPI name registration** (finding 5 — urgent) and
the overlay name/boundary. Continue on `APPROVE GATE 1`.

### Phase 1 — Releases become boring (scenario S5)

1. Define `publishing-v5` as an immutable shared-workflow contract; leave
   v3/v4 tags in place; migrate callers batch by batch.
2. Introduce release-PR automation (Release Please or equivalent) using the
   existing `pydevices-release-automation` GitHub App token (required so the
   created release triggers downstream workflows; plain `GITHUB_TOKEN` does
   not). The release PR carries `VERSION` and `CHANGELOG.md`; the human
   version choice happens in PR review (section 4.2).
3. Pilot on the Gate 1 pilot repo as a dry run; nothing publishes until Brad
   merges the generated PR.
4. Add branch protection and required checks to the publishing repositories
   before any auto-merge behavior exists.
5. Configure production PyPI pending Trusted Publishers for the approved
   names, with a protected `pypi` environment. Production publication itself
   still requires explicit per-package approval (rule 7).
6. Stand up the **Release Health dashboard** (one maintained issue or page:
   version, tag, Release, assets, TestPyPI/PyPI, MIP, downstream run status)
   *before* any automatic publishing is enabled.
7. Attach release assets. Fix the workbench tag contract per the Gate 1
   decision. Serialize the lvgl-bindings sync (finding 3) and document the
   single-writer rule where a contributor would trip on it. Label or clean up
   the stale TestPyPI leaves (finding 13).
8. Roll out to the remaining publishers (`pdwidgets`, `pygraphics`,
   `pydevices` + `pydevices-desktop`, `mpftp`, `audioif` — the last only in
   coordination with its in-flight plan, rule 9) in batches of at most five.

#### Gate 2 — Release approval

Present: S5 evidence on the pilots (dry-run transcript, dashboard live, a real
TestPyPI release end to end), protection/ruleset previews, rollback notes.
Continue on `APPROVE GATE 2`.

### Phase 2 — Standalone builds and patch ownership (scenarios S1, S2)

1. Make the native pilot own its public build glue: `micropython.mk` /
   `micropython.cmake` / manifest, declared and pinned dependencies (ulab,
   Adafruit_MP3), feature flags, dependency checks with early failures, and a
   clean-build test. Its patch queue owns the Adafruit_MP3 Windows patch.
2. Create the runtime overlay repository (only as approved at Gate 1):
   the versioned home for the Windows networking/SSL/select patches, Windows
   FFI, the WebAssembly port additions and external variant, wasmbridge,
   fetch support, and wasm locking. Pinned upstream release; ordered mailbox
   series; disposable-worktree builds; per-profile tests; provenance recording
   patch checksums and source revisions; scheduled compatibility checks
   against supported upstreams. Initial profiles: `windows-networked`,
   `windows-full`, `desktop-pydevices`, `webassembly-pydevices`. Release ids
   of the form `mp-v1.28.0-pydevices.1`. Publishing overlay *binaries* is a
   separate approval from publishing the overlay source.
3. Declare the CircuitPython oracle pin in a checked-in location with an
   `apply_cp_patches.sh --status` mismatch warning (finding 10) — without
   moving the pin (section 4.2) and in coordination with the audioif plan.
4. Add drift checks for committed generated artifacts (finding 11).
5. Present the interpreter-binary distribution proposal (finding 12); execute
   only Brad's decision.
6. Convert cmods to delegate: its build commands call the public contracts.
   Prove every pilot build passes with cmods absent from the machine.

#### Gate 3 — Standalone approval

Present: S1 and S2 passing with evidence on the pilots; cmods-absent proof;
cmods delegation demo; the overlay's first green scheduled compatibility run;
patch provenance table. Continue on `APPROVE GATE 3`.

### Phase 3 — The stranger's walkthrough (scenarios S4, S6)

1. README and quickstart pass for every active repository, governed by the
   existing `doc-style.md`; support status and boundary stated; feature flags
   and optional dependencies documented where they gate behavior.
2. Examples exercised in CI where the simulator or unix port makes it
   feasible; the rest marked as hardware-verified with the board named.
3. Organization presence: landing page, descriptions, topics, status labels,
   pinned repositories, consistent lifecycle signals; redirects for the
   retired URLs (finding 7); PyDevices.github.io aligned with all of it.

#### Gate 4 — Presentation approval

Present: S4 evidence (a cold-run transcript per pilot-class repo), the S6
walk recorded, before/after of the organization landing. Continue on
`APPROVE GATE 4`.

### Phase 4 — Portfolio rollout

Apply the proven contracts to every remaining in-scope repository in batches
of at most five, choosing per-archetype what applies (a template repo does not
get a patch queue; an app gets a dependency manifest and bootstrap). Every
repository ends with an explicit role, lifecycle label, dependency contract,
clean validation path, and release status — or a recorded exception with an
owner and exit criteria. Standard checkpoint packet at each batch boundary.

#### Gate 5 — Portfolio approval

Present: the contract matrix (done / remaining / excepted), final ownership
maps for patches and integration assets, cmods scope statement, dashboard
showing the whole portfolio. Continue on `APPROVE GATE 5`.

### Phase 5 — Optional cockpit (supports S7)

With execution in the cloud, no agent needs a Codespace: the executor brings
its own sandbox and bootstraps from the workspace manifest, which exists from
Phase 0 (section 2.1). This phase covers only Brad's optional hands-on
browser environment; his default cockpit is GitHub itself — PR review plus
the Release Health dashboard.

1. If wanted: a devcontainer that inherits the same workspace manifest — one
   environment definition with two consumers, never a parallel procedure.
2. Health checks for missing tools, repositories, and credentials.
3. Document agent and credential boundaries: what each agent kind (cloud
   executor, workstation session, review bots) can see, what is deliberately
   withheld, and how its output enters review. Agents never hold release
   credentials in any environment.
4. Local WSL/Linux use remains first-class. If a repository build works only
   inside the cockpit, that is a Phase 2 regression.

#### Gate 6 — Cockpit approval

Present: rebuild-from-manifest evidence, local-parity evidence, credential
boundary documentation, recurring cost estimate. Continue on `APPROVE GATE 6`.

### Phase 6 — Optional public changes

Only on explicit fresh approval, executed one pilot action at a time with a
stop after the first: production-publication automation policy beyond the
human merge gate; any archival; any rename or transfer (also requires lifting
the section 1 name freeze). Approval of one action never authorizes another.

### Phase 7 — Handoff and standing review (scenario S7)

1. Runbooks: release, rollback, incident, bot-failure recovery, onboarding
   another maintainer or agent.
2. A concise recurring-maintenance calendar (upstream pin reviews, patch
   compatibility, dependency policy, dashboard review).
3. **The standing cold-eyes review**: a scheduled (quarterly, or per major
   release) re-run of scenarios S1, S4, S5, and S6 on a rotating sample of
   repositories, filed as an issue with findings. The bar decays without
   enforcement; this is the enforcement.
4. Final evidence pack: S1–S7 current, exceptions ledger current, list of
   actions that still require Brad personally.

The program is complete only when Brad accepts the handoff.

## 8. Ownership rules (for every phase)

1. Component-specific integration assets live in the component repository.
2. Runtime-wide patches and variants live in the overlay.
3. Shared tooling is extracted only when it has multiple real consumers and a
   stable interface.
4. Maintainer-only experiments may stay in cmods if labeled and not required
   by any supported public build.
5. No patch, variant, or glue file has two undocumented source-of-truth
   copies. `lvgl-bindings` remains the single writer for its sync targets.

## 9. Definition of done

The program is done when the seven scenarios pass with current evidence
across the portfolio (per-archetype applicability decided at Gate 5), the
exceptions ledger is complete and each exception is documented where a
stranger would otherwise misread it, the standing review is scheduled, and
Brad has approved every gate and the handoff.

Equivalently: an expert applying either lens to any in-scope repository, or
to the organization entire, finds only decisions — never accidents.

## 10. Standard checkpoint packet

At every gate and batch boundary:

1. Outcome first.
2. Scope completed, scope remaining.
3. Files, PRs, settings, or external objects changed.
4. Scenario evidence (which scenarios, exact commands, results).
5. Failures, exceptions, and uncertainty — stated plainly.
6. Security, publication, and cost implications.
7. Rollback procedure.
8. Exceptions-ledger changes proposed.
9. At most five decisions requested from Brad, and the exact approval phrase
   required to continue.
