#!/usr/bin/env python3
"""Build every dynamic PyDevices Python distribution from lib/ and utils/."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DEBRIS = {"__pycache__", "README.md", "build", "dist"}
# No internal dependency table here: with lib/ shipped as one distribution the
# graph between its components is internal imports, not package requirements.
# synchronize_mip_package.py still needs it, because MIP publishes each
# component separately.
# See synchronize_mip_package.py: the desktop distribution ships utils/ plus
# the desktop board config directory, both taken whole.
DESKTOP_DIR = "board_configs/desktop"


def publishable(path: Path) -> bool:
    return (
        not path.name.startswith(".")
        and path.name not in DEBRIS
        and path.suffix not in {".pyc", ".pyo"}
        and (path.is_dir() or path.suffix == ".py")
    )


def components(directory: Path) -> list[Path]:
    return sorted((path for path in directory.iterdir() if publishable(path)), key=lambda path: path.name)


def copy_component(source: Path, destination: Path) -> None:
    if source.is_dir():
        # Mirrors ignore_debris in synchronize_mip_package.py: the top level is
        # gated by publishable(), everything nested is gated here.
        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns(".*", "__pycache__", "*.pyc", "*.pyo", "*.metadata.json"),
        )
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def project_text(name: str, version: str, description: str, dependencies: list[str], source: Path) -> str:
    modules = sorted(path.stem for path in source.glob("*.py") if path.name != "__init__.py")
    module_line = f"py-modules = {modules!r}\n" if modules else ""
    dependency_lines = "\n".join(f'  "{dependency}",' for dependency in dependencies)
    return f'''[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "{version}"
description = "{description}"
readme = "README.md"
requires-python = ">=3.9"
license = "MIT"
authors = [{{ name = "Brad Barnett" }}]
dependencies = [
{dependency_lines}
]

[project.urls]
Homepage = "https://github.com/PyDevices/pydevices"
Repository = "https://github.com/PyDevices/pydevices"

[tool.setuptools]
package-dir = {{ "" = "src" }}
{module_line}
[tool.setuptools.packages.find]
where = ["src"]
'''


def write_project(stage: Path, name: str, version: str, description: str, dependencies: list[str]) -> None:
    stage.mkdir(parents=True, exist_ok=True)
    (stage / "src").mkdir(exist_ok=True)
    (stage / "README.md").write_text(f"# {name}\n\n{description}.\n", encoding="utf-8")
    (stage / "pyproject.toml").write_text(
        project_text(name, version, description, dependencies, stage / "src"), encoding="utf-8"
    )


def build(root: Path, output: Path, version: str) -> None:
    work = output / "work"
    dist = output / "dist"
    if output.exists():
        shutil.rmtree(output)
    work.mkdir(parents=True)
    dist.mkdir()

    leaves = components(root / "lib")
    leaf_names = [path.stem if path.is_file() else path.name for path in leaves]
    if len(leaf_names) != len(set(leaf_names)):
        raise SystemExit("lib/ contains colliding module and package names")

    # One distribution holding all of lib/, not one per component. On a desktop
    # nobody installs a single leaf, and the per-leaf shape produced eight
    # distributions pinned to each other with ==version, all of which had to be
    # republished in lockstep. MIP stays granular because flash is scarce there;
    # pip has no such constraint.
    stages: list[Path] = []
    meta = work / "pydevices"
    meta_src = meta / "src"
    for source in leaves:
        copy_component(source, meta_src / source.name)
    write_project(
        meta,
        "pydevices",
        version,
        "Portable display, audio, event, and timing foundations for PyDevices",
        [],
    )
    stages.append(meta)

    desktop = work / "pydevices-desktop"
    desktop_source = desktop / "src"
    for source in components(root / "utils"):
        copy_component(source, desktop_source / source.name)
    for source in components(root / DESKTOP_DIR):
        copy_component(source, desktop_source / source.name)
    write_project(
        desktop,
        "pydevices-desktop",
        version,
        "Complete PyDevices desktop runtime and board configuration",
        [f"pydevices=={version}"],
    )
    stages.append(desktop)

    for stage in stages:
        subprocess.run(
            [sys.executable, "-m", "build", str(stage), "--outdir", str(dist)],
            check=True,
        )
    subprocess.run([sys.executable, "-m", "twine", "check", *map(str, sorted(dist.iterdir()))], check=True)
    print(f"Built {len(stages)} distributions covering {len(leaves)} lib components.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repository", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    build(args.source_repository.resolve(), args.output.resolve(), args.version)


if __name__ == "__main__":
    main()
