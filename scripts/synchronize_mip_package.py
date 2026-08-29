#!/usr/bin/env python3
"""Synchronize a single-source PyDevices package into the MIP repository."""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Profile:
    package: str
    description: str
    pypi_name: str | None
    requirements: tuple[tuple[str, str], ...] = ()


PROFILES = {
    "palettes": Profile(
        package="palettes",
        description="Color palette toolkit for PyDevices (wheel, cube, material_design)",
        pypi_name="pydevices-palettes",
    ),
    "pdwidgets": Profile(
        package="pdwidgets",
        description="Cross-platform widget toolkit for PyDevices",
        pypi_name="pydevices-pdwidgets",
        # No cross-repository requirements. micropython-lib resolves require()
        # by inclusion at build time, so these three shipped all of pydevices,
        # pygraphics, and palettes inside the pdwidgets package -- 212 files
        # for a widget toolkit. Removed until build.py can emit real install
        # time deps; see "Planned: real MIP dependencies" in
        # docs/publishing-automation.md.
        #
        # The PyPI side keeps proper dependencies in pdwidgets/pyproject.toml;
        # only MIP loses them.
        requirements=(),
    ),
    "pygraphics": Profile(
        package="pygraphics",
        description=(
            "Pure-Python pygraphics for MicroPython/CircuitPython/CPython "
            "(FrameBuffer, Draw, fonts); import as pygraphics"
        ),
        pypi_name=None,
    ),
    # audioif is the first source repository with more than one publishable
    # package, which is why mip-profile takes a list. Its native modules are
    # firmware (a usermod, not MIP); these two are the pure-Python tier on top.
    #
    # Both carry pypi_name=None deliberately. They do reach PyPI, but inside
    # the pydevices-audioif wheel rather than as distributions of their own, so
    # claiming a pypi_publish here would advertise a name pip cannot resolve --
    # the same reasoning as the PYPI_DISTRIBUTIONS note further down.
    #
    # No requirements either: audioinstruments and audioeffects both import
    # audioif's native modules, which arrive with the firmware and are not MIP
    # packages, so there is no edge for require() to express.
    "audioinstruments": Profile(
        package="audioinstruments",
        description=(
            "53 synthio instruments for PyDevices (drum machines and "
            "synthesizers); import as audioinstruments"
        ),
        pypi_name=None,
    ),
    "audioeffects": Profile(
        package="audioeffects",
        description=(
            "Effect classes for PyDevices audio (delay, drive, dynamics, eq, "
            "modulation, pitch, reverb); import as audioeffects"
        ),
        pypi_name=None,
    ),
}

PROFILE_REPOSITORIES = {
    "palettes": "PyDevices/palettes",
    "pdwidgets": "PyDevices/pdwidgets",
    "pygraphics": "PyDevices/pygraphics",
    "pydevices": "PyDevices/pydevices",
    "audioinstruments": "PyDevices/audioif",
    "audioeffects": "PyDevices/audioif",
}

# No internal dependency table: lib/ ships as a single MIP package, so the graph
# between its components is imports rather than package requirements. It was
# needed while each component was published separately.
# The desktop package ships utils/ plus the desktop board config. Both are
# whole directories, so there is nothing to enumerate: publishable() already
# filters README.md, package.json, and __pycache__ out of the latter.
# boarddev.py used to be listed here too, before it moved into lib/ and became
# a package of its own.
PYDEVICES_DESKTOP_DIR = "board_configs/desktop"


def ignore_debris(_directory: str, names: list[str]) -> set[str]:
    # publishable() gates the top level; this gates everything nested inside a
    # package directory, which copytree would otherwise take wholesale. That is
    # how four *.metadata.json editor artifacts once shipped inside appdev.
    ignored = {"__pycache__", "build", "dist"}
    return {
        name
        for name in names
        if name.startswith(".")
        or name in ignored
        or name.endswith((".pyc", ".pyo", ".metadata.json"))
    }


def render_manifest(profile: Profile, version: str) -> str:
    lines = [
        "metadata(",
        f'    description={profile.description!r},',
        f'    version="{version}",',
        '    author="Brad Barnett",',
        '    license="MIT",',
    ]
    if profile.pypi_name:
        lines.append(f'    pypi_publish="{profile.pypi_name}",')
    lines.append(")")
    for mip_name, pypi_name in profile.requirements:
        lines.append(f'require("{mip_name}", pypi="{pypi_name}")')
    lines.append(f'package("{profile.package}")')
    lines.append("")
    return "\n".join(lines)


def publishable(path: Path) -> bool:
    return (
        not path.name.startswith(".")
        and path.name not in {"__pycache__", "README.md", "build", "dist"}
        and path.suffix not in {".pyc", ".pyo"}
        and (path.is_dir() or path.suffix == ".py")
    )


def copy_component(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination, ignore=ignore_debris)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


# The only two PyDevices distributions on PyPI. Every lib/ component ships
# inside "pydevices", so a leaf manifest must not claim a pypi_publish of its
# own -- pydevices-appdev and friends stopped existing when pip collapsed to
# one distribution, and naming them here would advertise something unpublished.
PYPI_DISTRIBUTIONS = {"pydevices", "pydevices-desktop"}


def render_pydevices_manifest(name: str, version: str, requirements: tuple[str, ...], payloads: tuple[str, ...] = ()) -> str:
    lines = [
        "metadata(",
        f'    description="PyDevices {name}",',
        f'    version="{version}",',
        '    author="Brad Barnett",',
        '    license="MIT",',
    ]
    if name in PYPI_DISTRIBUTIONS:
        lines.append(f'    pypi_publish="{name}",')
    lines.append(")")
    lines.extend(f'require("{requirement}")' for requirement in requirements)
    lines.extend(payloads)
    lines.append("")
    return "\n".join(lines)


def synchronize_pydevices(source_root: Path, mip_root: Path, version: str) -> None:
    destination_root = mip_root / "micropython" / "pydevices"
    if destination_root.parent != mip_root / "micropython":
        raise SystemExit(f"refusing unexpected MIP destination: {destination_root}")
    if destination_root.exists():
        shutil.rmtree(destination_root)
    destination_root.mkdir(parents=True)

    # One package for the whole of lib/, matching the PyPI distribution.
    # Publishing a package per component bought nothing: micropython-lib
    # resolves require() by inclusion at build time, not as a dependency edge,
    # so the index materialised every component's files into each package that
    # required it -- installing two of them wrote the shared files twice.
    package = destination_root / "pydevices"
    package.mkdir()
    payloads: list[str] = []
    names: list[str] = []
    for source in sorted(filter(publishable, (source_root / "lib").iterdir()), key=lambda path: path.name):
        names.append(source.stem if source.is_file() else source.name)
        copy_component(source, package / source.name)
        payloads.append(f'module("{source.name}")' if source.is_file() else f'package("{source.name}")')

    if len(names) != len(set(names)):
        raise SystemExit("lib/ contains colliding module and package names")

    (package / "manifest.py").write_text(
        render_pydevices_manifest("pydevices", version, (), tuple(payloads)), encoding="utf-8"
    )

    desktop = destination_root / "pydevices-desktop"
    desktop.mkdir()
    desktop_payloads: list[str] = []
    for source in sorted(filter(publishable, (source_root / "utils").iterdir()), key=lambda path: path.name):
        copy_component(source, desktop / source.name)
        desktop_payloads.append(f'module("{source.name}")' if source.is_file() else f'package("{source.name}")')
    for source in sorted(filter(publishable, (source_root / PYDEVICES_DESKTOP_DIR).iterdir()), key=lambda path: path.name):
        copy_component(source, desktop / source.name)
        desktop_payloads.append(f'module("{source.name}")' if source.is_file() else f'package("{source.name}")')
    manifest = render_pydevices_manifest("pydevices-desktop", version, ("pydevices",))
    manifest += "\n".join(desktop_payloads) + "\n"
    (desktop / "manifest.py").write_text(manifest, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repository", required=True, type=Path)
    parser.add_argument("--source-repository-name", required=True)
    parser.add_argument("--mip-repository", required=True, type=Path)
    parser.add_argument("--profile", required=True, choices=sorted((*PROFILES, "pydevices")))
    parser.add_argument("--version", required=True)
    args = parser.parse_args()

    expected_repository = PROFILE_REPOSITORIES[args.profile]
    if args.source_repository_name != expected_repository:
        raise SystemExit(
            f"profile {args.profile!r} requires {expected_repository}, "
            f"not {args.source_repository_name}"
        )

    source_repository = args.source_repository.resolve()
    mip_root = args.mip_repository.resolve()
    if args.profile == "pydevices":
        synchronize_pydevices(source_repository, mip_root, args.version)
        return

    profile = PROFILES[args.profile]
    source = source_repository / "lib" / profile.package
    destination = mip_root / "micropython" / profile.package
    if not source.is_dir():
        raise SystemExit(f"package source does not exist: {source}")
    expected_parent = mip_root / "micropython"
    if destination.parent != expected_parent:
        raise SystemExit(f"refusing unexpected MIP destination: {destination}")

    if destination.exists():
        shutil.rmtree(destination)
    package_destination = destination / profile.package
    shutil.copytree(source, package_destination, ignore=ignore_debris)
    (destination / "manifest.py").write_text(render_manifest(profile, args.version))


if __name__ == "__main__":
    main()
