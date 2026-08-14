# Hand-Off Notes — PyDevices Organization Web Redesign & Centralized Architecture

## Current Status (Completed Above-the-Fold Redesign & Organization Consolidation)
We have completed the organization-wide web redesign, zero-exception site generator architecture, clean `.site/` filesystem harmonization, and centralized GitHub organization policies across all **16 PyDevices organization repositories**.

### Summary of Completed Features

1. **Centralized Database & Zero-Exception Generator (`.github`)**:
   - **Single Source of Truth Database**: [`dotgithub/data/repos_db.json`](file:///home/brad/gh/pydevices/dotgithub/data/repos_db.json) stores all metadata (eyebrows, headlines, descriptions, tier colors, and 4-button CTA layouts) for all 16 repositories.
   - **Unified Generator**: [`dotgithub/scripts/generate_sites.py`](file:///home/brad/gh/pydevices/dotgithub/scripts/generate_sites.py) updates all `.site/index.html` pages in < 0.2 seconds.
   - **Master Asset Vault & Auto-Sync**: Master logo [`dotgithub/assets/img/logo.svg`](file:///home/brad/gh/pydevices/dotgithub/assets/img/logo.svg) and chrome JS/CSS assets auto-sync to `.site/` in all 16 repositories during generation.
   - **Zero `if` Branches**: Uses 1 single template function for Above-the-Fold hero banners, head meta tags, and chrome asset syncing across all repositories. `PYDEVICES-PORTAL-GRIDS` is the single exception for rendering Tier 1–5 grid cards on the Org Portal page.

2. **Standardized Title & Relative Head Tags**:
   - All browser tab titles are standardized to `<title>PyDevices - <repo-name></title>`.
   - Relative favicon link `<link rel="icon" type="image/svg+xml" href="img/logo.svg">` across all pages.

3. **100% Uniform Filesystem Layout (`.site/`)**:
   - All landing page sources live inside `.site/index.html` with `.site/img/logo.svg`, `.site/vendor/pydevices-chrome/`, and `.site/.nojekyll`.
   - `PyDevices.github.io` source files live in `.site/index.html` matching all 15 subrepos 100%.

4. **Pristine Root & GitHub Actions Deployment**:
   - Cleaned all generated build artifacts (`index.html`, `img/`, `vendor/`, `assets/`) from `PyDevices.github.io` root.
   - Added automated GitHub Pages deployment workflow: [`PyDevices.github.io/.github/workflows/deploy.yml`](file:///home/brad/gh/pydevices/PyDevices.github.io/.github/workflows/deploy.yml) to deploy `.site/` on push.

5. **Organization Workflow Standardization**:
   - Standardized all GitHub Pages deployment workflows to **`deploy.yml`** across 14 repositories.
   - Standardized all unit test workflows to **`tests.yml`** and documentation workflows to **`docs.yml`**.

6. **Centralized Organization Policies in `.github`**:
   - Added [`dotgithub/SECURITY.md`](file:///home/brad/gh/pydevices/dotgithub/SECURITY.md) (Security vulnerability reporting policy inherited by all 16 repos).
   - Added [`dotgithub/profile/README.md`](file:///home/brad/gh/pydevices/dotgithub/profile/README.md) (Organization profile overview shown on GitHub homepage).

---

## Deferred Items for Next Session (Pick-Up Points)

1. **Below-the-Fold Content Review**:
   - Inspect lower section components across landing pages (feature grids, specs, code blocks, tables).

2. **PyScript Gallery Revamp (Phase 3)**:
   - Overhaul the PyScript gallery generator in `pydevices-examples`.
   - Re-architect gallery card layouts, live runner sandboxes, and MIP package imports.
