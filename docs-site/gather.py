# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Bring every library's docs into this folder, so one Sphinx run builds them.

Each repository in ``libraries.toml`` is cloned (one commit, from ``main``)
into ``_repos/<repo>``, and each library's docs folder is copied in as
``<slug>``. A copy, not a link: Sphinx follows a link to the file it points
at, and the page's links to its neighbours would then miss. Read the Docs
runs this before the build; run it yourself before a local build:

    python docs-site/gather.py
    sphinx-build -b html docs-site docs-site/_build/html

``--local NAME=PATH`` uses a checkout you already have instead of a clone, so
a change you are making shows up in the site before it is pushed (run it
again after you edit a page):

    python docs-site/gather.py --local pygraphics=../pygraphics

``--site DIR`` gathers for another site that keeps its own ``libraries.toml``,
such as the tools' site in ``tools-docs-site``:

    python docs-site/gather.py --site tools-docs-site
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent


def libraries(site: Path):
    with open(site / "libraries.toml", "rb") as f:
        return tomllib.load(f)["library"]


def clone(repo: str, dest: Path, ref: str) -> None:
    if dest.is_symlink() or dest.is_file():
        dest.unlink()
    elif dest.exists():
        shutil.rmtree(dest)
    url = f"https://github.com/{repo}.git"
    subprocess.run(
        ["git", "clone", "--quiet", "--depth", "1", "--single-branch", "--branch", ref, url, str(dest)],
        check=True,
    )
    head = subprocess.run(["git", "-C", str(dest), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True)
    print(f"{repo} {ref} at {head.stdout.strip()}")


def copy_docs(dest: Path, docs: Path) -> None:
    if dest.is_symlink() or dest.is_file():
        dest.unlink()
    elif dest.exists():
        if not (dest / ".gathered").exists():
            raise SystemExit(f"{dest} is a folder gather.py didn't make; move it and run again")
        shutil.rmtree(dest)
    shutil.copytree(docs, dest, ignore=shutil.ignore_patterns("_build", "__pycache__"))
    (dest / ".gathered").write_text(f"copied from {docs}\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--local", action="append", default=[], metavar="NAME=PATH",
        help="use the checkout at PATH for repository NAME (omnipython, pygraphics, ...)",
    )
    parser.add_argument("--ref", default="main", help="branch to clone (default: main)")
    parser.add_argument(
        "--site", default=str(HERE), metavar="DIR",
        help="the site folder holding libraries.toml (default: this script's folder)",
    )
    args = parser.parse_args(argv)

    local = {}
    for item in args.local:
        name, sep, path = item.partition("=")
        if not sep:
            parser.error(f"--local takes NAME=PATH, not {item!r}")
        local[name.split("/")[-1]] = Path(path).expanduser().resolve()

    site = Path(args.site).resolve()
    libs = libraries(site)
    repos = site / "_repos"
    repos.mkdir(exist_ok=True)
    for repo in dict.fromkeys(lib["repo"] for lib in libs):
        name = repo.split("/", 1)[1]
        dest = repos / name
        if name in local:
            if not (local[name] / ".git").exists():
                raise SystemExit(f"--local {name}: {local[name]} is not a git checkout")
            if dest.is_symlink() or dest.is_file():
                dest.unlink()
            elif dest.exists():
                shutil.rmtree(dest)
            dest.symlink_to(local[name], target_is_directory=True)
            print(f"{repo} from {local[name]}")
        else:
            clone(repo, dest, args.ref)
    unknown = set(local) - {lib["repo"].split("/", 1)[1] for lib in libs}
    if unknown:
        raise SystemExit(f"--local names a repository the site doesn't use: {', '.join(sorted(unknown))}")

    for lib in libs:
        docs = repos / lib["repo"].split("/", 1)[1] / lib.get("docs", "docs")
        if not (docs / "conf.py").is_file():
            raise SystemExit(f"{lib['repo']} has no {lib.get('docs', 'docs')}/conf.py")
        copy_docs(site / lib["slug"], docs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
