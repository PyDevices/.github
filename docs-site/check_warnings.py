# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Sort the site build's warnings by the repository whose file caused them.

    sphinx-build -b html --keep-going -w warnings.log docs-site docs-site/_build/html
    python docs-site/check_warnings.py warnings.log --repo PyDevices/pygraphics

Prints how many warnings each repository has. Each warning from the
repository named by ``--repo`` is printed as a GitHub annotation on its file,
and the exit status is 1 when there is at least one, so that repository's
check fails while the others' warnings are only counted. Warnings from the
site's own pages and from the shared theme belong to ``PyDevices/.github``,
and so do those Sphinx gives no file for, unless a traceback in the warning
names a library's file.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent  # the site folder; --site changes it
SITE = "PyDevices/.github"
LINE = re.compile(r"^(?:(?P<loc>.+?): )?(?P<level>WARNING|ERROR|CRITICAL): (?P<msg>.*)$")
PATH_LINE = re.compile(r"^(?P<path>/[^:]+?)(?::(?P<line>\d+))?(?::.*)?$")
TRACE = re.compile(r'File "(?P<path>/[^"]+)", line (?P<line>\d+)')


def libraries():
    with open(HERE / "libraries.toml", "rb") as f:
        return tomllib.load(f)["library"]


def owner(location: str, libs) -> tuple[str, str, str]:
    """The repository a warning belongs to, and its file and line there."""
    m = PATH_LINE.match(location or "")
    if not m:
        return SITE, "", ""
    path, line = m.group("path"), m.group("line") or ""
    for lib in libs:
        docs = lib.get("docs", "docs")
        repo_dir = HERE / "_repos" / lib["repo"].split("/", 1)[1]
        for base, prefix in ((HERE / lib["slug"], docs), (repo_dir.resolve() / docs, docs),
                             (repo_dir, ""), (repo_dir.resolve(), "")):
            base = str(base) + "/"
            if path.startswith(base):
                rel = path[len(base):]
                return lib["repo"], f"{prefix}/{rel}" if prefix else rel, line
    if path.startswith(str(HERE.parent) + "/"):
        return SITE, path[len(str(HERE.parent)) + 1:], line
    return SITE, path, line


def traced(msg: str, libs) -> tuple[str, str, str] | None:
    """For a warning with no file, the first library file its traceback names."""
    for m in TRACE.finditer(msg):
        repo, file, line = owner(f"{m.group('path')}:{m.group('line')}", libs)
        if repo != SITE:
            return repo, file, line
    return None


def read(log: Path, libs):
    warnings = []
    for raw in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE.match(raw)
        if m:
            warnings.append({"loc": m.group("loc") or "", "msg": m.group("msg"), "level": m.group("level")})
        elif warnings and raw.strip():
            warnings[-1]["msg"] += " " + raw.strip()
    for w in warnings:
        # An import that fails while autodoc reads a module (a missing system
        # library, say) is reported with no file; its traceback says whose it is.
        found = owner(w["loc"], libs) if w["loc"] else (traced(w["msg"], libs) or (SITE, "", ""))
        w["repo"], w["file"], w["line"] = found
    return warnings


def escape(text: str) -> str:
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def main(argv=None) -> int:
    global HERE
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("log", type=Path, help="the file sphinx-build -w wrote")
    parser.add_argument("--repo", default=SITE, help="the repository whose warnings fail the check (PyDevices/<name>)")
    parser.add_argument("--site", type=Path, default=None, metavar="DIR",
                        help="the site folder holding libraries.toml (default: this script's folder)")
    args = parser.parse_args(argv)
    if args.site is not None:
        HERE = args.site.resolve()

    libs = libraries()
    warnings = read(args.log, libs)
    counts = defaultdict(int)
    for w in warnings:
        counts[w["repo"]] += 1
    repos = [SITE] + list(dict.fromkeys(lib["repo"] for lib in libs))
    print("Warnings in the site build, by repository:")
    for repo in repos:
        print(f"  {repo}: {counts.get(repo, 0)}")

    mine = [w for w in warnings if w["repo"] == args.repo]
    for w in mine:
        where = f"file={w['file']}" + (f",line={w['line']}" if w["line"] else "") if w["file"] else ""
        print(f"::error {where}::{escape(w['msg'])}" if where else f"::error ::{escape(w['msg'])}")
    if mine:
        print(f"{len(mine)} warning(s) from {args.repo}; the site still builds, with these pages as they are.")
        return 1
    print(f"No warnings from {args.repo}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
