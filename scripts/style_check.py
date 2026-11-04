#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""Check the mechanical house-style rules in a repository.

Four rules, each one a thing a machine can judge:

1. Every Python file starts with the three SPDX lines (any holder).
2. No Sphinx roles or fields in a docstring (``:class:`X```, ``:param x:``).
3. No README or ``docs/`` page links to the ``.github`` repository.
4. The README has no badge row and no status banner.

Run it from a repository's root. With ``--base REF`` it checks only the files
changed since ``REF``; without it, every tracked file. Paths that are not ours
(vendored or generated code) go in ``.style-exclude`` at the root: one glob per
line, ``#`` for comments. A glob without a ``/`` matches a file name anywhere,
one with a ``/`` is anchored at the root, a trailing ``/`` takes a whole
directory, and ``**`` crosses folders.

Exit status is 1 when anything fails.
"""

import argparse
import ast
import os
import re
import subprocess
import sys

EXCLUDE_FILE = ".style-exclude"

SPDX_COPYRIGHT = re.compile(r"#\s*SPDX-FileCopyrightText:\s*\S")
SPDX_LICENSE = re.compile(r"#\s*SPDX-License-Identifier:\s*\S")

_ROLES = (
    "mod|func|meth|class|attr|data|const|exc|obj|ref|doc|term|any|"
    "paramref|envvar|samp|kbd|math|abbr|download|numref|py"
)
# :class:`X`, :py:func:`X`
ROLE = re.compile(rf"(?<![\w:])(:(?:{_ROLES})(?::\w+)?:`)")
# :param x:, :returns:, :type x: at the start of a line
_FIELDS = (
    "param|parameter|arg|argument|key|keyword|type|returns?|rtype|raises?|"
    "except|exception|var|ivar|cvar|vartype"
)
FIELD = re.compile(rf"^\s*(:(?:{_FIELDS})\b[^:\n]*:)", re.MULTILINE)

GITHUB_REPO_LINK = re.compile(
    r"(?:github\.com|githubusercontent\.com)/PyDevices/\.github(?![\w.-])", re.IGNORECASE
)

BANNER = re.compile(
    r"\b(?:alpha|beta|pre-?alpha|experimental|prototype)\s+(?:quality|software|release|stage)\b"
    r"|\bwork[- ]in[- ]progress\b"
    r"|\bunder\s+(?:heavy\s+|active\s+)?development\b"
    r"|\bnot\s+(?:yet\s+)?(?:ready|stable)\s+for\s+production\b"
    r"|^\s*(?:>\s*)?[*_]*(?:project\s+)?status[*_]*\s*:",
    re.IGNORECASE,
)
BADGE_HOSTS = (
    "shields.io|badgen.net|badge.svg|/badge/|badge.fury.io|pepy.tech|"
    "codecov.io|coveralls.io|readthedocs.org/projects|img.shields|"
    "travis-ci|circleci.com|app.codacy|snyk.io|libraries.io|api.reuse.software"
)
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
HTML_IMAGE = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)", re.IGNORECASE)
BADGE_URL = re.compile(BADGE_HOSTS, re.IGNORECASE)


def glob_to_regex(pattern):
    """Turn one exclude line into a compiled regex over root-relative paths."""
    anchored = "/" in pattern.rstrip("/")
    directory = pattern.endswith("/")
    pattern = pattern.strip("/")
    out = []
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif c == "*":
            out.append("[^/]*")
            i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    body = "".join(out)
    prefix = "" if anchored else "(?:.*/)?"
    tail = "/.*" if directory else "(?:/.*)?"
    return re.compile("^" + prefix + body + tail + "$")


def load_excludes(root):
    path = os.path.join(root, EXCLUDE_FILE)
    rules = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.split("#", 1)[0].strip()
                if line:
                    rules.append(glob_to_regex(line))
    return rules


def git_lines(root, *args):
    out = subprocess.run(
        ["git", "-C", root, *args], capture_output=True, text=True, check=True
    ).stdout
    return [line for line in out.split("\0" if "-z" in args else "\n") if line]


def list_files(root, base):
    """Return the root-relative paths to check, in sorted order."""
    if base:
        names = git_lines(root, "diff", "--name-only", "-z", "--diff-filter=ACMR", base + "...HEAD")
    else:
        try:
            names = git_lines(root, "ls-files", "-z")
        except (subprocess.CalledProcessError, FileNotFoundError):
            names = []
            for here, dirs, files in os.walk(root):
                dirs[:] = [d for d in dirs if d != ".git"]
                for name in files:
                    names.append(os.path.relpath(os.path.join(here, name), root).replace(os.sep, "/"))
    return sorted(n for n in names if os.path.isfile(os.path.join(root, n)))


def is_public_page(path):
    """A README at the root, or a Markdown page under docs/."""
    if "/" not in path:
        return path.lower().startswith("readme") and path.lower().endswith((".md", ".rst"))
    return path.startswith("docs/") and path.lower().endswith((".md", ".rst"))


def is_root_readme(path):
    return path.lower() in ("readme.md", "readme.rst")


def check_spdx(text):
    """One or more copyright lines, a bare ``#`` line, then the licence line.

    A shebang or a coding line may come first. Any holder passes, so a file that
    keeps its upstream holders alongside ours is fine.
    """
    lines = text.splitlines()
    i = 0
    if i < len(lines) and lines[i].startswith("#!"):
        i += 1
    if i < len(lines) and re.match(r"#.*coding[:=]", lines[i]):
        i += 1
    start = i
    while i < len(lines) and SPDX_COPYRIGHT.match(lines[i]):
        i += 1
    if i == start:
        return "does not start with the three SPDX lines (no SPDX-FileCopyrightText first)"
    if i >= len(lines) or lines[i].strip() != "#":
        return "SPDX lines need a bare '#' line between the copyright and the licence"
    if i + 1 >= len(lines) or not SPDX_LICENSE.match(lines[i + 1]):
        return "SPDX lines need the SPDX-License-Identifier line after the '#'"
    return None


def docstrings(tree):
    nodes = [tree]
    nodes += [n for n in ast.walk(tree)
              if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))]
    for node in nodes:
        doc = ast.get_docstring(node, clean=False)
        if doc is None:
            continue
        first = node.body[0]
        yield getattr(first, "lineno", 1), doc


def check_docstrings(text):
    """Return (line, message) for each Sphinx role or field, or a parse note."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError) as exc:
        return [], f"cannot parse ({exc.__class__.__name__}); docstrings not checked"
    found = []
    for lineno, doc in docstrings(tree):
        for pattern in (ROLE, FIELD):
            for m in pattern.finditer(doc):
                line = lineno + doc.count("\n", 0, m.start(1))
                kind = "role" if pattern is ROLE else "field"
                found.append((line, f"Sphinx {kind} in a docstring: {m.group(1)}"))
    return sorted(found), None


def check_page_links(text):
    found = []
    for n, line in enumerate(text.splitlines(), 1):
        if GITHUB_REPO_LINK.search(line):
            found.append((n, "link to the .github repository"))
    return found


def check_readme(text):
    found = []
    in_fence = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
        if in_fence:
            continue
        for url in IMAGE.findall(line) + HTML_IMAGE.findall(line):
            if BADGE_URL.search(url):
                found.append((n, f"badge image: {url}"))
        m = BANNER.search(line)
        if m:
            found.append((n, f"status banner: {m.group(0).strip()}"))
    return found


def read(root, path):
    with open(os.path.join(root, path), encoding="utf-8", errors="replace") as f:
        return f.read()


def run_checks(root, paths, skip_github_link=False):
    """Return (failures, notes): lists of (path, line, message)."""
    failures, notes = [], []
    for path in paths:
        lower = path.lower()
        if lower.endswith(".py"):
            text = read(root, path)
            if text.strip():
                msg = check_spdx(text)
                if msg:
                    failures.append((path, 1, msg))
            found, note = check_docstrings(text)
            failures += [(path, ln, msg) for ln, msg in found]
            if note:
                notes.append((path, 1, note))
        if is_public_page(path):
            text = read(root, path)
            if not skip_github_link:
                failures += [(path, ln, msg) for ln, msg in check_page_links(text)]
            if is_root_readme(path):
                failures += [(path, ln, msg) for ln, msg in check_readme(text)]
    return failures, notes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=".", help="repository root (default: here)")
    ap.add_argument("--base", help="check only files changed since this ref (merge-base diff)")
    ap.add_argument("--skip-github-link", action="store_true",
                    help="skip rule 3; the .github repository itself uses this")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)
    skip = args.skip_github_link or os.environ.get("GITHUB_REPOSITORY", "").endswith("/.github")

    excludes = load_excludes(root)
    paths = [p for p in list_files(root, args.base) if not any(r.match(p) for r in excludes)]
    failures, notes = run_checks(root, paths, skip)

    for path, ln, msg in notes:
        print(f"note: {path}: {msg}")
    for path, ln, msg in failures:
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::error file={path},line={ln}::{msg}")
        print(f"{path}:{ln}: {msg}")
    print(f"checked {len(paths)} files, {len(failures)} problems")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
