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
        'pydevices-examples': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6M9 12h6M9 15h4"/><circle cx="17" cy="15" r="1.5"/></svg>',
        'pygraphics': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a13 13 0 0 1 0 18 13 13 0 0 1 0-18z"/></svg>',
        'pdwidgets': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 8h10M7 12h6M7 16h8"/></svg>',
        'palettes': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/></svg>',
        'lvgl-bindings': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
        'lvgl-micropython': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 17V7l8-4 8 4v10l-8 4z"/><path d="M4 7l8 4 8-4M12 11v10"/></svg>',
        'lvgl-python': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a4 4 0 0 1 4 4v1h1a3 3 0 0 1 3 3v1a4 4 0 0 1-4 4h-1v1a4 4 0 0 1-4 4 4 4 0 0 1-4-4v-1H6a4 4 0 0 1-4-4v-1a3 3 0 0 1 3-3h1V6a4 4 0 0 1 4-4z"/></svg>',
        'lvgl-circuitpython': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v3M12 18v3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M3 12h3M18 12h3M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/><circle cx="12" cy="12" r="4"/></svg>',
        'pydevices-pyscript-template': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="14" rx="2"/><path d="M8 21h8M12 18v3"/><path d="M8 9h8M8 13h5"/></svg>',
        'pydevices-android-template': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="2" width="12" height="20" rx="2"/><path d="M10 19h4"/></svg>',
        'micropython-lib': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><path d="M3.3 7L12 12l8.7-5M12 22V12"/></svg>',
        'cmods': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l9 5v10l-9 5-9-5V7z"/><path d="M3 7l9 5 9-5M12 12v10"/></svg>',
        'mpftp': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="3" width="12" height="18" rx="2"/><path d="M9 7h6M9 11h6M9 15h4"/><circle cx="15" cy="15" r="1"/><path d="M15 16v3M13 19h4"/></svg>'
    }
    return icons.get(repo_name, '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/></svg>')

def get_tag_label(repo_name):
    tags = {
        'pydevices': 'Core Flagship',
        'displayif': 'C Bus Usermod',
        'pydevices-examples': 'Companion Showcase',
        'pygraphics': '0-Dependency',
        'pdwidgets': 'Pure-Python UI',
        'palettes': 'Color Engine',
        'lvgl-bindings': 'LVGL Generator',
        'lvgl-micropython': 'MicroPython C',
        'lvgl-python': 'CPython / Pyodide',
        'lvgl-circuitpython': 'CircuitPython C',
        'pydevices-pyscript-template': 'PWA Template',
        'pydevices-android-template': 'Android APK',
        'micropython-lib': 'MIP Index',
        'cmods': 'Build Tool',
        'mpftp': 'Workbench Tool'
    }
    return tags.get(repo_name, repo_name)

def build_head_tags_html(repo_name, data):
    display_title = f"PyDevices - {repo_name}"
    description = data.get('description', '')
    html = (
        f'  <!-- PYDEVICES-HEAD-TAGS: START -->\n'
        f'  <title>{display_title}</title>\n'
        f'  <meta name="description" content="{description}">\n'
        f'  <link rel="icon" type="image/svg+xml" href="img/logo.svg">\n'
        f'  <!-- PYDEVICES-HEAD-TAGS: END -->'
    )
    return html

def build_above_the_fold_html(repo_name, data):
    theme_color = data.get('theme_color', 'var(--tier-5-steel)')
    dark_gradient = get_gradient_dark(theme_color)
    eyebrow = data.get('eyebrow', repo_name)
    headline = data.get('headline', f'{repo_name} — PyDevices library.')
    description = data.get('description', '')

    button_html_list = []
    for btn in data.get('buttons', []):
        label = btn['label']
        href = btn['href']
        is_primary = btn.get('primary', False)
        
        if is_primary:
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

    html = (
        f'  <!-- PYDEVICES-ABOVE-THE-FOLD: START -->\n'
        f'  <div id="pydevices-site-header"></div>\n\n'
        f'  <!-- Hero Banner -->\n'
        f'  <section class="hero wrap">\n'
        f'    <div class="hero-lead">\n'
        f'      <div class="hero-brand">\n'
        f'        <div class="logo-badge product-mark" style="background: linear-gradient(135deg, {theme_color}, {dark_gradient});"><img src="img/logo.svg" alt="{repo_name}" width="112" height="112"></div>\n'
        f'        <span class="eyebrow" style="color: {theme_color};">{eyebrow}</span>\n'
        f'      </div>\n'
        f'      <h1>{headline}</h1>\n'
        f'    </div>\n'
        f'    <p><code>{repo_name}</code> {description}</p>\n'
        f'    <div class="cta">\n'
        f'{buttons_joined}\n'
        f'    </div>\n'
        f'  </section>\n'
        f'  <!-- PYDEVICES-ABOVE-THE-FOLD: END -->'
    )
    return html

def build_portal_grids_html(db):
    tier_meta = {
        1: ("1: Core Platform & Board Contract", "Standard hardware driver engine and companion reference code."),
        2: ("2: Pure-Python & Portable Toolkits", "Zero external native dependencies — runs on any Python 3 host."),
        3: ("3: LVGL Native Extensions & Binding Generator", "Single-source LVGL C header binding generator and native runtime modules."),
        4: ("4: Target App Hosts & PWA Templates", "Deploy PyDevices apps directly to desktop browsers or mobile APKs."),
        5: ("5: Developer Tools & Infrastructure", "MIP package indexing, multi-usermod builds, and serial/FTP IDE extensions.")
    }

    tier_repos = {1: [], 2: [], 3: [], 4: [], 5: []}
    for repo_name, data in db.items():
        if repo_name == 'PyDevices.github.io':
            continue
        tier = data.get('tier', 5)
        tier_repos[tier].append((repo_name, data))

    sections_html = []
    for tier in sorted(tier_repos.keys()):
        title, hint = tier_meta[tier]
        cards_html = []
        for repo_name, data in tier_repos[tier]:
            card_class = f'card-tier-{tier}'
            tag_class = f'tag-tier-{tier}'
            tag_label = get_tag_label(repo_name)
            icon_svg = get_card_icon(repo_name)
            desc = data.get('description', '')
            url = f'https://pydevices.github.io/{repo_name}/'

            c_html = (
                f'      <a class="card {card_class}" href="{url}">\n'
                f'        <div class="card-top">\n'
                f'          <span class="icon">{icon_svg}</span>\n'
                f'          <span class="tag {tag_class}">{tag_label}</span>\n'
                f'        </div>\n'
                f'        <h3>{repo_name}</h3>\n'
                f'        <p>{desc}</p>\n'
                f'        <span class="go">Visit site <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>\n'
                f'      </a>'
            )
            cards_html.append(c_html)

        cards_joined = '\n\n'.join(cards_html)
        sec_style = ' style="margin-top: 40px;"' if tier > 1 else ''

        sec_html = (
            f'    <!-- Tier {tier} Section -->\n'
            f'    <div class="section-head"{sec_style}>\n'
            f'      <h2>{title}</h2>\n'
            f'      <span class="hint">{hint}</span>\n'
            f'    </div>\n'
            f'    <div class="grid">\n'
            f'{cards_joined}\n'
            f'    </div>'
        )
        sections_html.append(sec_html)

    grids_joined = '\n\n'.join(sections_html)

    html = (
        f'  <!-- PYDEVICES-PORTAL-GRIDS: START -->\n'
        f'{grids_joined}\n'
        f'  <!-- PYDEVICES-PORTAL-GRIDS: END -->'
    )
    return html

def sync_assets(repo_name):
    # Zero-exception chrome asset sync: dotgithub/assets -> repo/.site/vendor/pydevices-chrome
    vendor_dir = os.path.join(BASE_DIR, repo_name, '.site/vendor/pydevices-chrome')
    img_dir = os.path.join(BASE_DIR, repo_name, '.site/img')
    os.makedirs(vendor_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    src_css = os.path.join(ASSETS_DIR, 'css/site.css')
    src_chrome = os.path.join(ASSETS_DIR, 'js/site-chrome.js')
    src_tree = os.path.join(ASSETS_DIR, 'js/tree-nav.js')
    src_theme = os.path.join(ASSETS_DIR, 'js/theme-toggle.js')
    src_logo = os.path.join(ASSETS_DIR, 'img/logo.svg')

    if os.path.exists(src_css): shutil.copy2(src_css, os.path.join(vendor_dir, 'site.css'))
    if os.path.exists(src_chrome): shutil.copy2(src_chrome, os.path.join(vendor_dir, 'site-chrome.js'))
    if os.path.exists(src_tree): shutil.copy2(src_tree, os.path.join(vendor_dir, 'tree-nav.js'))
    if os.path.exists(src_theme): shutil.copy2(src_theme, os.path.join(vendor_dir, 'theme-toggle.js'))
    
    # Auto-sync master logo.svg to .site/img/logo.svg
    if os.path.exists(src_logo): shutil.copy2(src_logo, os.path.join(img_dir, 'logo.svg'))

def update_head_tags(content, repo_name, data):
    new_head = build_head_tags_html(repo_name, data)
    head_pattern = re.compile(
        r'<!-- PYDEVICES-HEAD-TAGS: START -->.*?<!-- PYDEVICES-HEAD-TAGS: END -->',
        re.DOTALL
    )
    if head_pattern.search(content):
        return head_pattern.sub(new_head, content)
    
    head_match = re.search(r'<head[^>]*>', content, re.IGNORECASE)
    if head_match:
        c = re.sub(r'<title>.*?</title>', '', content, flags=re.IGNORECASE)
        c = re.sub(r'<meta\s+name="description"\s+content="[^"]*">', '', c, flags=re.IGNORECASE)
        c = re.sub(r'<link\s+rel="icon"[^>]*>', '', c, flags=re.IGNORECASE)
        head_match2 = re.search(r'<head[^>]*>', c, re.IGNORECASE)
        if head_match2:
            return c[:head_match2.end()] + '\n' + new_head + c[head_match2.end():]
    return content

def main():
    print("=== Pure Harmonized PyDevices Site Generator (.github) ===")
    
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)

    updated_sites = 0

    for repo_name, data in db.items():
        repo_dir = os.path.join(BASE_DIR, repo_name)
        if not os.path.exists(repo_dir):
            print(f"[SKIP] Repo dir not found: {repo_dir}")
            continue

        sync_assets(repo_name)

        site_html_path = os.path.join(repo_dir, '.site/landing/index.html') if repo_name == 'pydevices-examples' else os.path.join(repo_dir, '.site/index.html')
        if not os.path.exists(site_html_path):
            print(f"[SKIP] HTML file missing: {site_html_path}")
            continue

        with open(site_html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = update_head_tags(content, repo_name, data)

        new_above = build_above_the_fold_html(repo_name, data)
        marker_pattern = re.compile(
            r'<!-- PYDEVICES-ABOVE-THE-FOLD: START -->.*?<!-- PYDEVICES-ABOVE-THE-FOLD: END -->',
            re.DOTALL
        )

        if marker_pattern.search(content):
            content = marker_pattern.sub(new_above, content)
        else:
            body_match = re.search(r'<body[^>]*>', content, re.IGNORECASE)
            if body_match:
                insert_pos = body_match.end()
                content = content[:insert_pos] + '\n' + new_above + content[insert_pos:]

        # One Exception: Org Portal Grid Generation for PyDevices.github.io
        if repo_name == 'PyDevices.github.io':
            p_grids = build_portal_grids_html(db)
            marker_p_grids = re.compile(
                r'<!-- PYDEVICES-PORTAL-GRIDS: START -->.*?<!-- PYDEVICES-PORTAL-GRIDS: END -->',
                re.DOTALL
            )
            if marker_p_grids.search(content):
                content = marker_p_grids.sub(p_grids, content)

        # Cleanup duplicate hero sections outside the marker & normalize broken asset paths
        content = content.replace('src="assets/img/logo.svg"', 'src="img/logo.svg"')
        content = content.replace('href="https://pydevices.github.io/assets/img/logo.svg"', 'href="img/logo.svg"')
        content = content.replace('src="assets/js/site-chrome.js"', 'src="./vendor/pydevices-chrome/site-chrome.js"')
        content = content.replace('src="assets/js/theme-toggle.js"', 'src="./vendor/pydevices-chrome/theme-toggle.js"')
        content = content.replace('src="assets/js/tree-nav.js"', 'src="./vendor/pydevices-chrome/tree-nav.js"')
        rel_prefix = "../" if repo_name == "pydevices-examples" else "./"
        content = content.replace('src="https://pydevices.github.io/assets/js/site-chrome.js"', f'src="{rel_prefix}vendor/pydevices-chrome/site-chrome.js"')
        content = content.replace('src="https://pydevices.github.io/assets/js/theme-toggle.js"', f'src="{rel_prefix}vendor/pydevices-chrome/theme-toggle.js"')
        content = re.sub(r'src=["\']https://pydevices\.github\.io/assets/img/products/[^"\']+["\']', 'src="img/logo.svg"', content)

        if '<!-- PYDEVICES-ABOVE-THE-FOLD: END -->' in content:
            parts = content.split('<!-- PYDEVICES-ABOVE-THE-FOLD: END -->', 1)
            parts[1] = re.sub(r'<section\s+class=["\']hero\s+wrap["\']>.*?</section>', '', parts[1], flags=re.DOTALL | re.IGNORECASE)
            content = parts[0] + '<!-- PYDEVICES-ABOVE-THE-FOLD: END -->' + parts[1]

        with open(site_html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        updated_sites += 1
        print(f"[OK] Generated & Updated {repo_name} (.site/index.html)")

    print(f"=== Complete! Processed {len(db)} repos ({updated_sites} modified) ===")

if __name__ == '__main__':
    main()
