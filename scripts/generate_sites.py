#!/usr/bin/env python3
import json
import os
import re
import shutil

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
DOTGITHUB_DIR = os.path.join(BASE_DIR, 'dotgithub')
DB_PATH = os.path.join(DOTGITHUB_DIR, 'data/repos_db.json')
ASSETS_DIR = os.path.join(DOTGITHUB_DIR, 'assets')

def get_gradient_dark(color_var):
    mapping = {
        'var(--tier-1-amber)': '#d97706',
        'var(--tier-2-emerald)': '#059669',
        'var(--tier-3-blue)': '#2563eb',
        'var(--tier-4-purple)': '#7c3aed',
        'var(--tier-5-steel)': '#0284c7'
    }
    return mapping.get(color_var, '#0284c7')

def get_card_icon(repo_name):
    icons = {
        'pydevices': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>',
        'displayif': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M7 16l1-4M17 16l-1-4"/></svg>',
        'audioif': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10v4M8 7v10M12 4v16M16 7v10M20 10v4"/></svg>',
        'pydevices-examples': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6M9 12h6M9 15h4"/><circle cx="17" cy="15" r="1.5"/></svg>',
        'pygraphics': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a13 13 0 0 1 0 18 13 13 0 0 1 0-18z"/></svg>',
        'pdwidgets': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 8h10M7 12h6M7 16h8"/></svg>',
        'palettes': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/></svg>',
        'lvgl-bindings': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
        'lvgl-micropython': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 17V7l8-4 8 4v10l-8 4z"/><path d="M4 7l8 4 8-4M12 11v10"/></svg>',
        'lvgl-python': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a4 4 0 0 1 4 4v1h1a3 3 0 0 1 3 3v1a4 4 0 0 1-4 4h-1v1a4 4 0 0 1-4 4 4 4 0 0 1-4-4v-1H6a4 4 0 0 1-4-4v-1a3 3 0 0 1 3-3h1V6a4 4 0 0 1 4-4z"/></svg>',
        'lvgl-circuitpython': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v3M12 18v3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M3 12h3M18 12h3M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/><circle cx="12" cy="12" r="4"/></svg>',
        'pyscript-template': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="14" rx="2"/><path d="M8 21h8M12 18v3"/><path d="M8 9h8M8 13h5"/></svg>',
        'android-template': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="2" width="12" height="20" rx="2"/><path d="M10 19h4"/></svg>',
        'mip': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><path d="M3.3 7L12 12l8.7-5M12 22V12"/></svg>',
        'cmods': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l9 5v10l-9 5-9-5V7z"/><path d="M3 7l9 5 9-5M12 12v10"/></svg>',
        'mpftp': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="3" width="12" height="18" rx="2"/><path d="M9 7h6M9 11h6M9 15h4"/><circle cx="15" cy="15" r="1"/><path d="M15 16v3M13 19h4"/></svg>',
        # Same glyph as pydevices-examples -- these are sub-pages of that repo.
        'pydevices-examples-gallery': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6M9 12h6M9 15h4"/><circle cx="17" cy="15" r="1.5"/></svg>',
        'pydevices-examples-pyscript': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6M9 12h6M9 15h4"/><circle cx="17" cy="15" r="1.5"/></svg>',
    }
    return icons.get(repo_name, '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/></svg>')

def get_tag_label(repo_name):
    tags = {
        'pydevices': 'Core Flagship',
        'displayif': 'C Bus Usermod',
        'audioif': 'C Audio Usermod',
        'pydevices-examples': 'Companion Showcase',
        'pygraphics': '0-Dependency',
        'pdwidgets': 'Pure-Python UI',
        'palettes': 'Color Engine',
        'lvgl-bindings': 'LVGL Generator',
        'lvgl-micropython': 'MicroPython C',
        'lvgl-python': 'CPython / Pyodide',
        'lvgl-circuitpython': 'CircuitPython C',
        'pyscript-template': 'PWA Template',
        'android-template': 'Android APK',
        'mip': 'MIP Index',
        'cmods': 'Build Tool',
        'mpftp': 'IDE Extension'
    }
    return tags.get(repo_name, repo_name)

def validate_db(db):
    """Fail fast on a malformed database.

    The generator is run by hand, so this is where the check belongs -- it runs
    exactly when someone edits the database and regenerates.
    """
    if '_meta' not in db:
        raise SystemExit('repos_db.json is missing its _meta block')

    tiers = db['_meta']['tiers']
    problems = []
    for name, data in repos(db).items():
        # `is None`, not falsiness: the portal repo is legitimately tier 0.
        for field in ('tier', 'tier_name', 'description', 'buttons'):
            if data.get(field) is None:
                problems.append(f'{name}: missing {field}')
        tier = str(data.get('tier'))
        if tier not in tiers:
            problems.append(f'{name}: tier {tier} has no _meta.tiers entry')
        elif data.get('tier_name') != tiers[tier]['name']:
            problems.append(
                f'{name}: tier_name {data.get("tier_name")!r} disagrees with '
                f'_meta.tiers[{tier}].name {tiers[tier]["name"]!r}'
            )

        hero_canvas = data.get('hero_canvas')
        if hero_canvas is not None:
            if not isinstance(hero_canvas, dict):
                problems.append(f'{name}: hero_canvas must be an object')
            else:
                for req in ('app', 'width', 'height'):
                    if req not in hero_canvas:
                        problems.append(f'{name}: hero_canvas missing {req}')
                app_name = hero_canvas.get('app')
                app_path = os.path.join(ASSETS_DIR, 'apps', f'{app_name}.py')
                if app_name and not os.path.exists(app_path):
                    problems.append(f'{name}: hero_canvas app {app_name}.py not found in {os.path.relpath(app_path, BASE_DIR)}')

    valid_pages = {'portal-root', 'portal-subdir', 'self', 'self-subpath', 'none'}
    roots = [n for n, d in repos(db).items() if page_destination(d) == 'portal-root']
    for name, data in repos(db).items():
        destination = page_destination(data)
        if destination not in valid_pages:
            problems.append(
                f'{name}: page {destination!r} is not one of {sorted(valid_pages)}'
            )
        # A repo keeping its own Pages must still have somewhere to publish from.
        if destination == 'self' and not os.path.isdir(
            os.path.join(BASE_DIR, name, '.site')
        ):
            problems.append(f'{name}: page=self but no .site/ directory')
        if destination == 'self-subpath':
            site_repo = data.get('site_repo')
            site_subpath = data.get('site_subpath')
            if not site_repo or not site_subpath:
                problems.append(f'{name}: page=self-subpath needs site_repo and site_subpath')
            elif not os.path.isdir(os.path.join(BASE_DIR, site_repo, '.site', site_subpath)):
                problems.append(
                    f'{name}: page=self-subpath but no {site_repo}/.site/{site_subpath}/ directory'
                )
    if len(roots) != 1:
        problems.append(
            f'expected exactly one page=portal-root repo, found {roots or "none"}'
        )

    if problems:
        raise SystemExit('repos_db.json is invalid:\n  ' + '\n  '.join(problems))
    print(f"[OK] Database valid: {len(repos(db))} repos across {len(tiers)} tiers")


def repos(db):
    """Repository entries only; keys beginning with '_' are metadata."""
    return {k: v for k, v in db.items() if not k.startswith('_')}


def tier_meta(db):
    """{int tier: (name, hint)} from the database, not hardcoded here."""
    return {int(t): (m['name'], m['hint']) for t, m in db['_meta']['tiers'].items()}


def build_ecosystem_markdown(db):
    """The org repository map, emitted from the same database that drives the sites."""
    meta = tier_meta(db)
    by_tier = {}
    for repo_name, data in repos(db).items():
        if repo_name == 'PyDevices.github.io' or not data.get('portal_grid', True):
            continue
        by_tier.setdefault(data.get('tier', 5), []).append((repo_name, data))

    lines = [
        '<!-- PYDEVICES-ECOSYSTEM: START -->',
        '<!-- Generated by dotgithub/scripts/generate_sites.py from data/repos_db.json.',
        '     Do not edit between these markers; edit the database instead. -->',
        '',
    ]
    for tier in sorted(by_tier):
        name, hint = meta[tier]
        lines += [f'### Tier {tier}: {name}', '', f'{hint}', '']
        for repo_name, data in by_tier[tier]:
            url = f'https://github.com/PyDevices/{repo_name}'
            lines.append(f'- [`{repo_name}`]({url}) — {data.get("description", "")}')
        lines.append('')

    lines += ['**Deliberately absent from this map:**', '']
    for repo_name, reason in db['_meta']['excluded'].items():
        lines.append(f'- **{repo_name}** — {reason}')
    lines += ['', '<!-- PYDEVICES-ECOSYSTEM: END -->']
    return '\n'.join(lines)


ECOSYSTEM_TARGETS = (
    ('dotgithub', 'profile/README.md'),
    ('pydevices', 'docs/ecosystem.md'),
)


def write_ecosystem_markdown(db):
    """Rewrite the marker block in every consumer of the org map."""
    block = build_ecosystem_markdown(db)
    written = 0
    for repo_name, rel in ECOSYSTEM_TARGETS:
        path = os.path.join(BASE_DIR, repo_name, rel)
        if not os.path.exists(path):
            print(f"[SKIP] Ecosystem target missing: {path}")
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        updated = update_html_section(
            content,
            '<!-- PYDEVICES-ECOSYSTEM: START -->',
            '<!-- PYDEVICES-ECOSYSTEM: END -->',
            block,
        )
        if updated == content and '<!-- PYDEVICES-ECOSYSTEM: START -->' not in content:
            print(f"[SKIP] No ECOSYSTEM markers in {repo_name}/{rel}")
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(updated)
        written += 1
        print(f"[OK] Ecosystem map -> {repo_name}/{rel}")
    return written


def build_head_tags_html(repo_name, data):
    title = data.get('title', f'PyDevices - {repo_name}')
    return (
        f'  <!-- PYDEVICES-HEAD-TAGS: START -->\n'
        f'  <title>{title}</title>\n'
        f'  <meta name="description" content="{data.get("description", "")}">\n'
        f'  <link rel="icon" type="image/svg+xml" href="/assets/img/logo.svg">\n'
        f'  <!-- PYDEVICES-HEAD-TAGS: END -->'
    )

def build_above_the_fold_html(repo_name, data):
    # The hero shows the repo's own mark -- the same glyph as its portal card.
    # The portal keeps the org logo: it is the org's page, and get_card_icon
    # has no entry for it, so it would otherwise fall through to the generic
    # default. The glyphs are stroke="currentColor", hence color on the badge.
    mark = (
        '<img src="/assets/img/logo.svg" alt="PyDevices" width="112" height="112">'
        if page_destination(data) == 'portal-root'
        else get_card_icon(repo_name)
    )
    theme_color = data.get('theme_color', 'var(--tier-5-steel)')
    dark_gradient = get_gradient_dark(theme_color)
    eyebrow = data.get('eyebrow', repo_name)
    headline = data.get('headline', f'{repo_name} — PyDevices library.')
    description = data.get('description', '')
    # The org homepage and repo sub-pages (e.g. a gallery) aren't "a repo among
    # repos" -- skip the <code>reponame</code> prefix that every repo's own
    # top-level landing page uses to name itself.
    description_html = (
        description
        if page_destination(data) in ('portal-root', 'self-subpath')
        else f'<code>{repo_name}</code> {description}'
    )
    # Optional second hero paragraph (e.g. gallery pages' "click a card" note).
    hero_note = data.get('hero_note', '')

    button_html_list = []
    for btn in data.get('buttons', []):
        label, href = btn['label'], btn['href']
        if btn.get('primary', False):
            b_html = (
                f'      <a class="btn primary" style="background: #24292e; color: #fff; border-color: #24292e;" href="{href}">\n'
                f'        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.9a3.4 3.4 0 0 0-1-2.6c3-.3 6-1.5 6-6.5a5 5 0 0 0-1.4-3.5 4.6 4.6 0 0 0-.1-3.5s-1.1-.3-3.5 1.3a12 12 0 0 0-6 0C6.6 1.7 5.5 2 5.5 2a4.6 4.6 0 0 0-.1 3.5A5 5 0 0 0 4 9c0 5 3 6.2 6 6.5a3.4 3.4 0 0 0-1 2.6V22"/></svg>\n'
                f'        {label}\n'
                f'      </a>'
            )
        else:
            b_html = f'      <a class="btn" style="border-color: {theme_color}; color: {theme_color};" href="{href}">{label}</a>'
        button_html_list.append(b_html)

    buttons_joined = '\n'.join(button_html_list)

    hero_canvas = data.get('hero_canvas')
    if hero_canvas:
        app_name = hero_canvas.get('app', 'watch')
        width = hero_canvas.get('width', 240)
        height = hero_canvas.get('height', 240)
        shape = hero_canvas.get('shape', 'round')
        deps = hero_canvas.get('deps', ['pydevices', 'pydevices-lvgl'])
        deps_str = ','.join(deps)
        app_url = hero_canvas.get('app_url', f'https://PyDevices.github.io/assets/apps/{app_name}.py')
        canvas_id = 'hero_canvas'
        container_class = 'hero-canvas-circle' if shape == 'round' else 'hero-canvas-square'

        canvas_html = (
            f'    <div class="hero-canvas-wrap" data-hero-canvas="{canvas_id}" data-hero-app="{app_name}" data-hero-deps="{deps_str}" data-hero-app-url="{app_url}">\n'
            f'      <div class="{container_class}">\n'
            f'        <div class="hero-canvas-loader">\n'
            f'          <div class="hero-spinner"></div>\n'
            f'          <span class="hero-canvas-status">Live Pure-Python Device</span>\n'
            f'        </div>\n'
            f'        <canvas id="{canvas_id}" width="{width}" height="{height}" tabindex="0"></canvas>\n'
            f'      </div>\n'
            f'    </div>'
        )

        hero_note_html = f'      <p>{hero_note}</p>\n' if hero_note else ''
        cta_html = (
            f'      <div class="cta">\n{buttons_joined}\n      </div>\n' if buttons_joined else ''
        )
        return (
            f'  <!-- PYDEVICES-ABOVE-THE-FOLD: START -->\n'
            f'  <div id="pydevices-site-header"></div>\n\n'
            f'  <!-- Hero Banner -->\n'
            f'  <section class="hero wrap has-hero-canvas">\n'
            f'    <div class="hero-main">\n'
            f'      <div class="hero-lead">\n'
            f'        <div class="logo-badge product-mark" style="background: linear-gradient(135deg, {theme_color}, {dark_gradient}); color: #fff;">{mark}</div>\n'
            f'        <span class="eyebrow" style="color: {theme_color};">{eyebrow}</span>\n'
            f'      </div>\n'
            f'      <h1>{headline}</h1>\n'
            f'      <p>{description_html}</p>\n'
            f'{hero_note_html}'
            f'{cta_html}'
            f'    </div>\n'
            f'{canvas_html}\n'
            f'  </section>\n'
            f'  <!-- PYDEVICES-ABOVE-THE-FOLD: END -->'
        )

    hero_note_html = f'    <p>{hero_note}</p>\n' if hero_note else ''
    cta_html = (
        f'    <div class="cta">\n{buttons_joined}\n    </div>\n' if buttons_joined else ''
    )
    return (
        f'  <!-- PYDEVICES-ABOVE-THE-FOLD: START -->\n'
        f'  <div id="pydevices-site-header"></div>\n\n'
        f'  <!-- Hero Banner -->\n'
        f'  <section class="hero wrap">\n'
        f'    <div class="hero-lead">\n'
        f'      <div class="hero-brand">\n'
        f'        <div class="logo-badge product-mark" style="background: linear-gradient(135deg, {theme_color}, {dark_gradient}); color: #fff;">{mark}</div>\n'
        f'        <span class="eyebrow" style="color: {theme_color};">{eyebrow}</span>\n'
        f'      </div>\n'
        f'      <h1>{headline}</h1>\n'
        f'    </div>\n'
        f'    <p>{description_html}</p>\n'
        f'{hero_note_html}'
        f'{cta_html}'
        f'  </section>\n'
        f'  <!-- PYDEVICES-ABOVE-THE-FOLD: END -->'
    )

def build_portal_grids_html(db):
    meta = tier_meta(db)

    tier_repos = {1: [], 2: [], 3: [], 4: [], 5: []}
    for repo_name, data in repos(db).items():
        if repo_name != 'PyDevices.github.io' and data.get('portal_grid', True):
            tier_repos[data.get('tier', 5)].append((repo_name, data))

    sections_html = []
    for tier in sorted(tier_repos.keys()):
        name, hint = meta[tier]
        title = f'{tier}: {name}'
        cards_html = []
        for repo_name, data in tier_repos[tier]:
            cards_html.append(
                f'      <a class="card card-tier-{tier}" href="/{repo_name}/">\n'
                f'        <div class="card-top">\n'
                f'          <span class="icon">{get_card_icon(repo_name)}</span>\n'
                f'          <span class="tag tag-tier-{tier}">{get_tag_label(repo_name)}</span>\n'
                f'        </div>\n'
                f'        <h3>{repo_name}</h3>\n'
                f'        <p>{data.get("description", "")}</p>\n'
                f'        <span class="go">Visit site <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>\n'
                f'      </a>'
            )

        cards_joined = '\n\n'.join(cards_html)
        sec_style = ' style="margin-top: 40px;"' if tier > 1 else ''

        sections_html.append(
            f'    <!-- Tier {tier} Section -->\n'
            f'    <div class="section-head"{sec_style}>\n'
            f'      <h2>{title}</h2>\n'
            f'      <span class="hint">{hint}</span>\n'
            f'    </div>\n'
            f'    <div class="grid">\n'
            f'{cards_joined}\n'
            f'    </div>'
        )

    return (
        f'  <!-- PYDEVICES-PORTAL-GRIDS: START -->\n'
        f'{"\n\n".join(sections_html)}\n'
        f'  <!-- PYDEVICES-PORTAL-GRIDS: END -->'
    )


PORTAL_REPO = 'PyDevices.github.io'

# Written only when a portal subdirectory has no page yet; every run then
# rewrites the marker blocks in place, so this is a one-time scaffold.
PAGE_SKELETON = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- PYDEVICES-HEAD-TAGS: START -->
  <!-- PYDEVICES-HEAD-TAGS: END -->
  <link rel="stylesheet" href="/assets/chrome/site.css">
</head>
<body>
  <!-- PYDEVICES-ABOVE-THE-FOLD: START -->
  <!-- PYDEVICES-ABOVE-THE-FOLD: END -->
  <div id="pydevices-site-footer"></div>
  <script src="/assets/chrome/site-chrome.js"></script>
</body>
</html>
'''


def asset_prefix(data):
    """Prefix for shared-asset URLs in this repo's page."""
    return '/'


def page_destination(data):
    """Where this repo's landing page is written.

    'portal-root'   the portal's own index.html
    'portal-subdir' PyDevices.github.io/<portal_path or repo>/index.html
    'self'          the repo's own .site/index.html, for repos that still
                    publish their own Pages because they serve real payload
    'self-subpath'  <site_repo>/.site/<site_subpath>/index.html -- a
                    sub-page of another repo's own Pages (e.g. a gallery),
                    generated as a database entry but excluded from the
                    portal grid/ecosystem map via portal_grid: false. The
                    rest of that page (its own GEN:* marker blocks) stays
                    owned by that repo's own generator.
    'none'          no generated page; the repo keeps only its portal card
    """
    return data.get('page', 'portal-subdir')


def _copy_chrome_into(site_root):
    chrome_dir = os.path.join(site_root, 'assets/chrome')
    img_dir = os.path.join(site_root, 'assets/img')
    os.makedirs(chrome_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    for fname in ('site.css', 'site-chrome.js', 'theme-toggle.js', 'hero-runtime.js', 'docs-runtime.js'):
        src = os.path.join(ASSETS_DIR, 'js' if fname.endswith('.js') else 'css', fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(chrome_dir, fname))

    for img_name in ('logo.svg', 'logo-512.png', 'logo-avatar.png'):
        src_img = os.path.join(ASSETS_DIR, 'img', img_name)
        if os.path.exists(src_img):
            shutil.copy2(src_img, os.path.join(img_dir, img_name))


def sync_assets(db):
    """Copy the shared chrome and apps to the portal repository root (PyDevices.github.io)."""
    portal_root = os.path.join(BASE_DIR, PORTAL_REPO)
    _copy_chrome_into(portal_root)

    # Sync static standalone apps into portal assets/apps/
    apps_src = os.path.join(ASSETS_DIR, 'apps')
    if os.path.exists(apps_src):
        portal_apps = os.path.join(portal_root, 'assets/apps')
        os.makedirs(portal_apps, exist_ok=True)
        for app_file in os.listdir(apps_src):
            shutil.copy2(os.path.join(apps_src, app_file), os.path.join(portal_apps, app_file))

    # The first-party PyScript template is intentionally Pyodide-only and is
    # published beneath its generated portal landing page. Keep its complete
    # offline PWA payload together, including the pinned vendored interpreter.
    template_pwa = os.path.join(BASE_DIR, 'pyscript-template', 'pwa')
    if os.path.isdir(template_pwa):
        shutil.copytree(
            template_pwa,
            os.path.join(portal_root, 'pyscript-template', 'pwa'),
            dirs_exist_ok=True,
        )

def update_html_section(content, marker_start, marker_end, new_html):
    # Consume any existing indentation before the start marker. The replacement
    # carries its own, so without this every run prepends another level and the
    # marker drifts right forever.
    pattern = re.compile(
        r'[ \t]*' + re.escape(marker_start) + r'.*?' + re.escape(marker_end),
        re.DOTALL,
    )
    if pattern.search(content):
        # A lambda, not a string: the replacement is arbitrary HTML/markdown and
        # must never be scanned for backreference escapes.
        return pattern.sub(lambda _m: new_html, content)
    return content

def get_site_html_path(repo_name, data):
    """Absolute path of the index.html this repo's entry writes, or None."""
    destination = page_destination(data)
    portal = os.path.join(BASE_DIR, PORTAL_REPO)
    if destination == 'portal-root':
        return os.path.join(portal, 'index.html')
    if destination == 'portal-subdir':
        return os.path.join(portal, data.get('portal_path', repo_name), 'index.html')
    if destination == 'self':
        return os.path.join(BASE_DIR, repo_name, '.site/index.html')
    if destination == 'self-subpath':
        return os.path.join(BASE_DIR, data['site_repo'], '.site', data['site_subpath'], 'index.html')
    return None

def main():
    print("=== Pure Harmonized PyDevices Site Generator (.github) ===")
    
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)

    validate_db(db)

    updated_sites = 0

    sync_assets(db)

    for repo_name, data in repos(db).items():
        site_html_path = get_site_html_path(repo_name, data)
        if site_html_path is None:
            print(f"[SKIP] {repo_name}: no generated page (page=none)")
            continue

        # A portal subdirectory is ours to create; a repo's own .site is not.
        if page_destination(data) in ('portal-root', 'portal-subdir'):
            os.makedirs(os.path.dirname(site_html_path), exist_ok=True)
            if not os.path.exists(site_html_path):
                with open(site_html_path, 'w', encoding='utf-8') as f:
                    f.write(PAGE_SKELETON)
                print(f"[NEW] Created {os.path.relpath(site_html_path, BASE_DIR)}")

        if not os.path.exists(site_html_path):
            print(f"[SKIP] HTML file missing: {site_html_path}")
            continue

        with open(site_html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update section markers cleanly
        # A page with no marker blocks is not a page this generator manages --
        # report it rather than claiming success. pydevices sat like this for
        # months after its landing page was replaced by a redirect stub.
        missing = [
            marker for marker in ('PYDEVICES-HEAD-TAGS', 'PYDEVICES-ABOVE-THE-FOLD')
            if f'<!-- {marker}: START -->' not in content
        ]
        if missing:
            print(f"[WARN] {repo_name}: no {', '.join(missing)} marker block -- nothing written")
            continue

        content = update_html_section(content, '<!-- PYDEVICES-HEAD-TAGS: START -->', '<!-- PYDEVICES-HEAD-TAGS: END -->', build_head_tags_html(repo_name, data))
        content = update_html_section(content, '<!-- PYDEVICES-ABOVE-THE-FOLD: START -->', '<!-- PYDEVICES-ABOVE-THE-FOLD: END -->', build_above_the_fold_html(repo_name, data))

        if repo_name == 'PyDevices.github.io':
            content = update_html_section(content, '<!-- PYDEVICES-PORTAL-GRIDS: START -->', '<!-- PYDEVICES-PORTAL-GRIDS: END -->', build_portal_grids_html(db))

        # Remove a duplicate hero section left outside the marker block.
        marker = '<!-- PYDEVICES-ABOVE-THE-FOLD: END -->'
        if marker in content:
            head, tail = content.split(marker, 1)
            tail = re.sub(r'<section\s+class=["\']hero\s+wrap["\']>.*?</section>', '', tail, flags=re.DOTALL | re.IGNORECASE)
            content = head + marker + tail

        with open(site_html_path, 'w', encoding='utf-8') as f:
            f.write(content)

        updated_sites += 1
        print(f"[OK] Generated & Updated {repo_name} ({os.path.relpath(site_html_path, BASE_DIR)})")

    written = write_ecosystem_markdown(db)

    print(f"=== Complete! Processed {len(repos(db))} repos "
          f"({updated_sites} sites, {written} ecosystem maps) ===")

if __name__ == '__main__':
    main()
