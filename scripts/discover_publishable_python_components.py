#!/usr/bin/env python3
"""Discover public leaf distributions from a source directory.

Every non-debris top-level file or directory is a component. Directories keep
their name; files use their stem. The command deliberately has no component
allowlist so adding content changes the next release inventory automatically.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

IGNORED_NAMES = {"__pycache__", "README.md", "build", "dist"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def is_publishable(path: Path) -> bool:
    return (
        not path.name.startswith(".")
        and path.name not in IGNORED_NAMES
        and path.suffix.lower() not in IGNORED_SUFFIXES
        and (path.is_dir() or path.suffix == ".py")
    )


def discover(source: Path) -> list[dict[str, str]]:
    if not source.is_dir():
        raise SystemExit(f"source directory does not exist: {source}")

    components: list[dict[str, str]] = []
    names: dict[str, Path] = {}
    for path in sorted(source.iterdir(), key=lambda item: item.name):
        if not is_publishable(path):
            continue
        name = path.name if path.is_dir() else path.stem
        if name in names:
            raise SystemExit(
                f"component name collision: {names[name].name!r} and {path.name!r} both map to {name!r}"
            )
        names[name] = path
        components.append(
            {
                "name": name,
                "path": path.as_posix(),
                "kind": "directory" if path.is_dir() else "file",
            }
        )
    return components


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--format", choices=("json", "names"), default="json")
    args = parser.parse_args()

    components = discover(args.source)
    if args.format == "names":
        for component in components:
            print(component["name"])
    else:
        print(json.dumps(components, indent=2))


if __name__ == "__main__":
    main()
