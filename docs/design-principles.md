# PyDevices Design Principles

Org-wide standards that every PyDevices design — module, library, protocol
surface, or tool — is measured against before it ships. Repo-specific
conventions live in each repo; these apply everywhere.

## 1. Completeness: no stranded endpoints

> **Any pairing the protocols permit that the design does not deliver is a
> defect in the design, not a feature request.**

If two endpoints speak the same protocol, they interoperate — full stop.
A Bluetooth MIDI controller talks to a USB MIDI synthesizer; a USB DAW
drives a wireless instrument; every input transport feeds the same event
system and every MIDI transport the same message model, so the full mesh
of pairings falls out of the architecture instead of being built pair by
pair. Nobody reviewing a PyDevices design should ever be able to say
"well, it *could* do this, but it doesn't."

What this demands in practice:

- **Design for the mesh, not the pair.** Policy — event mapping, message
  models, component graphs — lives once, in a shared layer, with each
  transport or backend a provider beneath it. When routing is the default
  outcome of the architecture, completeness is cheap; when it's a feature
  per pairing, it's already lost.
- **Deliver what's possible; record what isn't, with the honest reason.**
  Some pairings are closed by silicon, by an upstream stack that doesn't
  exist yet, or by physics. Those exclusions are stated in the design
  document with their cause — "excluded by silicon, not policy" — never
  silently assumed. An undocumented gap is indistinguishable from an
  unfinished design.
- **Prove it live.** Every claimed pairing is backed by a demonstration a
  stranger could watch. A matrix cell nobody has exercised is a claim,
  not a capability.

This standard was first written down in the `btif` vision (2026-08-31)
and applies retroactively to everything the organization ships: when a
gap in an existing surface is found, it is triaged as a defect.

## 2. Portability by tier

Surfaces are as portable as the platforms allow, and honest about where
they can't be: complete on the primary target, present everywhere it
makes sense, and translated — not duplicated — where a sibling ecosystem
already has its own excellent idioms. Exceptions are recorded in the
design document, not assumed. Every platform claim carries its proof
tier — bench-proven, CI-proven, or community-verified — as defined in
[`platform-support-tiers.md`](platform-support-tiers.md).

## 3. Identity varies with capability, deterministically

When software can change what a device *is* at runtime — the USB
interface set a host enumerates, the BLE profile set a peer discovers —
the device's advertised identity must change with it. Hosts cache
associations (drivers, pairings, settings) against identity: two
different capability sets sharing one identity poison that cache, and
the failure lands on someone else's machine, later, unattributably.

And the variation must be **deterministic** — the same capability set
always yields the same identity — so a host's cached association stays
correct across reboots and re-enumerations. Fifteen configurations,
fifteen identities, the same fifteen every time.

Proven in usbif's runtime function selection (2026-08-31), where
TinyUSB's own source warns of exactly this; the obligation is inherited
by every PyDevices surface that lets Python vary a device's capability
set.

---

*New principles are added here when they've been proven in a shipped
design, not before. Suggest one via
[Discussions](https://github.com/PyDevices/pydevices/discussions).*
