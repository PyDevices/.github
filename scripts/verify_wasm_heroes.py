#!/usr/bin/env python3
"""Verify every published hero app actually runs.

The hero demos fail silently: the page renders, the runtime catches its own
exception, and nothing anywhere goes red. The `/pydevices/` hero was dead for
a week before a human happened to look. This turns that class of failure into
a check.

It reads the runtime's own verdict rather than inferring one. `hero-runtime.js`
publishes `window.__pydevicesHeroes` as `{phase, heroes, errors}` — a single
top-level `phase` ("idle" until it settles, then "ready" or "failed"), the
launched heroes, and any errors it caught. Read those fields individually:
the object holds live emscripten FS nodes, so JSON-serialising the whole
thing throws on a circular reference.

Pages are derived from data/repos_db.json, never hardcoded, so a hero added
there is checked without touching this file.

Usage:
    python3 scripts/verify_wasm_heroes.py [--base URL] [--json PATH]

Exits non-zero if any hero is missing, failed, or never became ready.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = REPO_ROOT / "data" / "repos_db.json"
DEFAULT_BASE = "https://pydevices.github.io"

# How long a hero may take to boot before silence counts as failure. The wasm
# runtime downloads and instantiates before it can report anything; a short
# wait produces confident false failures.
SETTLE_MS = 30_000
POLL_MS = 500


def hero_pages(db: dict) -> list[tuple[str, str]]:
    """(repo, path) for every entry declaring a hero, in database order."""
    pages = []
    for name, data in db.items():
        if not isinstance(data, dict) or not data.get("hero_canvas"):
            continue
        page = data.get("page")
        if page == "none":
            continue
        if page == "portal-root":
            pages.append((name, "/"))
        else:
            # Everything else is checked at its portal path, including
            # page='self' repos that publish from their own GitHub Pages.
            # Those URLs resolve under the portal domain and their heroes are
            # live, so excluding them would mean silently covering less than
            # the database declares. If one is shadowed or missing, that is a
            # finding ('no-hero-on-page'), not a reason to skip it.
            pages.append((name, f"/{data.get('portal_path') or name}/"))
    return pages


def check(page_url: str, browser) -> dict:
    """Load one page and return the runtime's own verdict."""
    ctx = browser.new_context(viewport={"width": 1200, "height": 800})
    pg = ctx.new_page()
    errors: list[str] = []
    pg.on("pageerror", lambda e: errors.append(str(e)[:300]))

    def on_console(msg):
        if msg.type == "error":
            try:
                errors.append(" ".join(str(a.json_value()) for a in msg.args)[:300])
            except Exception:  # noqa: BLE001 - reading a console arg must never abort the check
                errors.append(msg.text[:300])

    pg.on("console", on_console)

    result = {"url": page_url, "status": "unknown", "phase": None, "errors": errors}
    try:
        pg.goto(page_url, wait_until="networkidle", timeout=60_000)
    except Exception as exc:  # noqa: BLE001 - the reason is the finding
        result["status"] = "unreachable"
        errors.append(f"navigation: {exc}"[:300])
        ctx.close()
        return result

    # A page that declares no hero at all is a finding in itself: the portal
    # believes it has one. This is how a repo enabling its own GitHub Pages
    # silently shadows the generated page (workbench, 2026-09-01).
    declared = pg.eval_on_selector_all("[data-hero-canvas]", "els => els.length")
    if declared == 0:
        result["status"] = "no-hero-on-page"
        ctx.close()
        return result

    waited = 0
    phase = None
    while waited < SETTLE_MS:
        phase = pg.evaluate("() => (window.__pydevicesHeroes || {}).phase")
        if phase in ("ready", "failed"):
            break
        pg.wait_for_timeout(POLL_MS)
        waited += POLL_MS

    result["phase"] = phase
    result["hero_count"] = pg.evaluate(
        "() => ((window.__pydevicesHeroes || {}).heroes || []).length"
    )
    for e in pg.evaluate(
        "() => ((window.__pydevicesHeroes || {}).errors || []).map(String).slice(0, 3)"
    ):
        errors.append(e[:300])

    if phase is None:
        result["status"] = "no-runtime-state"
    elif phase == "failed":
        result["status"] = "failed"
    elif phase == "ready":
        result["status"] = "ready"
    else:
        result["status"] = "never-ready"
    ctx.close()
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default=os.environ.get("HERO_BASE", DEFAULT_BASE))
    ap.add_argument("--json", type=Path, help="write the full result set here")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    db = json.loads(DB_PATH.read_text(encoding="utf-8"))
    pages = hero_pages(db)
    if not pages:
        print("no hero pages declared in repos_db.json", file=sys.stderr)
        return 2

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for repo, path in pages:
            r = check(args.base.rstrip("/") + path, browser)
            r["repo"] = repo
            results.append(r)
            mark = "ok  " if r["status"] == "ready" else "FAIL"
            print(f"{mark} {repo:24} {r['status']}")
            if r["status"] != "ready" and r["errors"]:
                print(f"       {r['errors'][0]}")
        browser.close()

    if args.json:
        args.json.write_text(json.dumps(results, indent=2), encoding="utf-8")

    bad = [r for r in results if r["status"] != "ready"]
    print(f"\n{len(results) - len(bad)}/{len(results)} heroes ready")
    if bad:
        print("\nnot ready:")
        for r in bad:
            first = r["errors"][0] if r["errors"] else ""
            print(f"  {r['repo']}: {r['status']} — {first}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
