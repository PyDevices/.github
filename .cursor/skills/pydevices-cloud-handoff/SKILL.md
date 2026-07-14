---
name: pydevices-cloud-handoff
description: >-
  Hand off PyDevices work from Cursor desktop to Cloud Agents using the
  gh/pydevices multi-repo workspace. Use when the user asks to run on cloud,
  move to cloud, hand off to cloud, or delegate a PyDevices task to a cloud
  agent while keeping the symlink layout under ~/gh/pydevices.
---

# PyDevices cloud handoff

## Before handoff (desktop)

1. **Commit or stash** local changes on branches the cloud agent should continue.
2. In the **Agents** input, choose **Run on → Cloud** (or **Move to Cloud** on an
   existing session).
3. Select the saved environment **Pydevices Cloud Workspace** (or the team
   equivalent with all PyDevices repos).
4. Prefer starting from **`PyDevices/.github`** or **`PyDevices/cmods`** so
   `.cursor/environment.json` runs `scripts/cloud-workspace-install.sh` on boot.
5. Add a short line to the task prompt:

   ```
   Follow PyDevices/.github AGENTS.md for the gh/pydevices workspace layout.
   ```

6. Then state the actual task (build target, bug, PR scope, etc.).

## What the cloud agent gets

- Repos cloned under `/agent/repos/` by the saved environment.
- On install: `~/gh/pydevices/` symlinks and `cmods/` interior (see
  `scripts/cloud-workspace-install.sh`).
- Layout rules in repo root **`AGENTS.md`** (this repository).

## What is not handed off

- Your Mac’s `~/gh/` tree (symlinks are recreated on the VM).
- `micropython-lib` (not part of this workspace; GH Actions owns it).

## After handoff

- Cloud agent works on a branch; review the PR or check out the branch locally.
- **Move to Local** may require an existing local agent for the same repo.

## If layout looks wrong on the VM

Re-run manually from any PyDevices repo checkout:

```bash
bash scripts/cloud-workspace-install.sh
```

Or read `AGENTS.md` in this repo for the full tree and LVGL symlink rules.
