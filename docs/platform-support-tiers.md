# Platform Support Tiers

How PyDevices states what a platform claim is worth. Companion to
[`design-principles.md`](design-principles.md): the completeness standard
demands that every claim be proven or recorded with its honest cause —
these tiers are the vocabulary for doing that consistently, org-wide.

Every platform claim in a PyDevices README, vision, or roadmap carries
one of three labels:

## Bench-proven

We demonstrated it ourselves on real hardware — the demo a stranger
could watch exists and has run. This is the default tier for the
platforms on our bench: the MCU fleet (ESP32 family, RP2), Windows, and
desktop Linux.

## CI-proven

Continuous integration builds it, imports it, and runs its unit and
contract tests — but no one here has exercised it against real hardware
or OS services beyond what a runner provides. CI-proven is a real,
honest tier, not a lesser apology: structural correctness is proven,
hardware behavior is not yet, and the claim says so.

## Community-verified

The surface ships, clearly labeled as awaiting verification from
someone with the hardware. This tier is an invitation, not a gap: the
work is done to the CI-proven line, the seams are designed and
documented, and a report from the field — "works here," with platform
details — promotes the claim. Verification reports are welcome as
issues on the relevant repo or in
[Discussions](https://github.com/PyDevices/pydevices/discussions).

A claim may only sit in this tier if the two below it are actually met:
shipping untestable code and calling it community-verified is the
silent gap the completeness standard condemns, with a friendlier label.

---

## Current postures

**macOS.** PyDevices ships everything for macOS that CI can prove —
wheels, imports, unit and contract tests on macOS runners — and claims
nothing hardware-adjacent (USB enumeration, Bluetooth radios, audio
devices) beyond that. Those surfaces ship at the community-verified
tier: the code paths exist where the underlying libraries support them,
and reports from Mac users promote them. No PyDevices claim assumes a
Mac on our bench, because there isn't one.

**Single-board computers (Raspberry Pi and kin).** An SBC running
CPython on Linux inherits most of the desktop tier as-is: Bluetooth
via BlueZ, USB host enumeration, kmsdrm display output, standard
wheels. Those claims are the desktop Linux claims, at desktop Linux's
tier. The named gap is the machine layer — GPIO/SPI/I2C access that
would let MCU-style device drivers run on an SBC's pins. That seam is
identified and undelivered; it ships no claim today, and if it becomes
a project it starts at CI-proven with community verification invited
on the breadth of boards no bench could hold.

---

*Postures are updated here when a tier changes — a promotion needs its
verification report or bench demo; a demotion needs its honest cause.*
