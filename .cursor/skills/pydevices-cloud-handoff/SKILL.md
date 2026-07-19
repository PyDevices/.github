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
3. Prefer starting from **`PyDevices/.github`** so `.cursor/environment.json`
   runs the boot install scripts. A saved multi-repo environment (e.g.
   **Pydevices Cloud Workspace**) is nice-to-have for faster boots / token
   scope, but not required — the install scripts clone missing siblings.
4. State the actual task directly (build target, bug, PR scope, which files to
   open). Do **not** open a chat whose only job is “setup workspace” — boot
   install should already have produced `~/gh/pydevices/`.

   Optional one-liner if the agent is unfamiliar with the layout:

   ```
   Follow PyDevices/.github AGENTS.md for the gh/pydevices workspace layout.
   ```

## What the cloud agent gets

- On install (`scripts/cloud-workspace-install.sh` +
  `scripts/cloud-python-deps.sh`):
  - Sibling repos under `/agent/repos/` (cloned if Cursor did not materialize
    them; `repositoryDependencies` mainly expands GitHub token scope).
  - `~/gh/pydevices/` symlinks and `cmods/` interior (MP/CP shallow clones,
    LVGL submodule + `lv_cpython_mod/lvgl` symlink).
  - Python venvs for `pydisplay` / `palettes` / `pdwidgets` (apt-installs
    `python3-venv` + `libsdl2-dev` when the snapshot lacks them).
- Layout rules in repo root **`AGENTS.md`** (this repository).

## What is not handed off

- Your Mac’s `~/gh/` tree (symlinks are recreated on the VM).
- `micropython-lib` (not part of this workspace; GH Actions owns it).

## After handoff

- Cloud agent works on a branch; review the PR or check out the branch locally.
- **Move to Local** may require an existing local agent for the same repo.

## If layout looks wrong on the VM

Re-run both scripts from this repo’s checkout (idempotent):

```bash
bash scripts/cloud-workspace-install.sh && bash scripts/cloud-python-deps.sh
```

Or read `AGENTS.md` in this repo for the full tree and LVGL symlink rules.
