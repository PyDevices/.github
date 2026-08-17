#!/usr/bin/env python3
"""Build every dynamic PyDevices Python distribution from lib/ and utils/."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DEBRIS = {"__pycache__", "README.md", "build", "dist"}
INTERNAL_REQUIREMENTS = {
    "displaydev": ("events", "keys"),
    "eventsys": ("events", "keys", "multimer"),
}
DESKTOP_FILES = {
    "board_configs/desktop/board_config.py": "board_config.py",
    "board_configs/desktop/board_peripherals.py": "board_peripherals.py",
    "drivers/boarddev.py": "boarddev.py",
}


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
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".*", "__pycache__", "*.pyc", "*.pyo"))
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
authors = [{{ name = "Brad Barnett", email = "contact@pydevices.com" }}]
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

    stages: list[Path] = []
    for source, leaf in zip(leaves, leaf_names, strict=True):
        stage = work / leaf
        target = stage / "src" / (source.name if source.is_file() else leaf)
        copy_component(source, target)
        requirements = [f"pydevices-{dependency}=={version}" for dependency in INTERNAL_REQUIREMENTS.get(leaf, ())]
        write_project(stage, f"pydevices-{leaf}", version, f"PyDevices {leaf}", requirements)
        stages.append(stage)

    meta = work / "pydevices"
    write_project(
        meta,
        "pydevices",
        version,
        "Portable display, audio, event, and timing foundations for PyDevices",
        [f"pydevices-{leaf}=={version}" for leaf in leaf_names],
    )
    stages.append(meta)

    desktop = work / "pydevices-desktop"
    desktop_source = desktop / "src"
    for source in components(root / "utils"):
        copy_component(source, desktop_source / source.name)
    for source_name, destination_name in DESKTOP_FILES.items():
        copy_component(root / source_name, desktop_source / destination_name)
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
    print(f"Built {len(stages)} distributions from {len(leaves)} dynamic lib components.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repository", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    build(args.source_repository.resolve(), args.output.resolve(), args.version)


if __name__ == "__main__":
    main()
