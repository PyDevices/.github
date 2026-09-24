#!/usr/bin/env python3
"""Synchronize a single-source PyDevices package into the MIP repository."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import tomllib
from pydevices_package_metadata import PYDEVICES_DESCRIPTIONS


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
    # audiodsp is the first source repository with more than one publishable
    # package, which is why mip-profile takes a list. Its native modules are
    # firmware (a usermod, not MIP); these two are the pure-Python tier on top.
    #
    # Both carry pypi_name=None deliberately. They do reach PyPI, but inside
    # the pydevices-audiodsp wheel rather than as distributions of their own, so
    # claiming a pypi_publish here would advertise a name pip cannot resolve --
    # the same reasoning as the PYPI_DISTRIBUTIONS note further down.
    #
    # No requirements either: audioinstruments and audioeffects both import
    # audiodsp's native modules, which arrive with the firmware and are not MIP
    # packages, so there is no edge for require() to express.
    "audioinstruments": Profile(
        package="audioinstruments",
        description=(
            "55 synthio instruments for PyDevices (drum machines and "
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

# The source repository for each profile is pydevices-lock.json in the MIP
# checkout, not a second map in this script. reusable-synchronize-mip-package.yml
# already keeps that lockfile on the runner; a hardcoded PROFILE_REPOSITORIES
# table disagreed with it after the audiodsp/audiocomponents split and blocked
# every publication until a new publishing-tools tag (#35).
LOCKFILE_NAME = "pydevices-lock.json"

# No internal dependency table: lib/ ships as a single MIP package, so the graph
# between its components is imports rather than package requirements. It was
# needed while each component was published separately.
# The desktop package ships utils/ plus the desktop board config. Both are
# whole directories, so there is nothing to enumerate: publishable() already
# filters README.md, package.json, and __pycache__ out of the latter.
# boarddev.py used to be listed here too, before it moved into lib/ and became
# a package of its own.
PYDEVICES_DESKTOP_DIR = "board_configs/desktop"


def lockfile_repository(mip_root: Path, profile: str) -> str:
    """Return the GitHub repository the MIP lockfile names for *profile*.

    A new profile is added to the lockfile deliberately, not auto-created.
    """
    lockfile = mip_root / LOCKFILE_NAME
    if not lockfile.is_file():
        raise SystemExit(f"{lockfile} is missing; add {profile!r} to {LOCKFILE_NAME} before publishing")
    try:
        lock = json.loads(lockfile.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{lockfile} is not valid JSON: {exc}") from exc
    if not isinstance(lock, dict) or profile not in lock:
        raise SystemExit(f"{profile!r} is not in {lockfile}; add it before publishing")
    entry = lock[profile]
    if not isinstance(entry, dict) or not entry.get("repository"):
        raise SystemExit(f"{profile!r} in {lockfile} has no repository")
    return str(entry["repository"])


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
    try:
        description = PYDEVICES_DESCRIPTIONS[name]
    except KeyError:
        raise SystemExit(f"no shared description for {name!r}") from None
    lines = [
        "metadata(",
        f"    description={description!r},",
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


#: Declares which modules of lib/ cannot run on a microcontroller. Its own
#: header says why and what the rules are; this reads it.
MIP_SPLIT_FILE = "mip-split.toml"


def read_host_only(source_root: Path) -> dict[str, frozenset[str]]:
    """{package: host-only module stems}, checked against what is on disk."""
    split_path = source_root / MIP_SPLIT_FILE
    if not split_path.exists():
        return {}
    with split_path.open("rb") as handle:
        declared = tomllib.load(handle)

    host_only: dict[str, frozenset[str]] = {}
    for package, section in declared.items():
        package_dir = source_root / "lib" / package
        if not package_dir.is_dir():
            raise SystemExit(
                f"{MIP_SPLIT_FILE} names package {package!r}, which is not in lib/"
            )
        present = {path.stem for path in package_dir.glob("*.py")}
        names = frozenset(section.get("host-only", ()))
        # A stale name is the way this file rots: the module gets renamed, the
        # entry stops matching anything, and it silently ships to the MCU again.
        missing = sorted(names - present)
        if missing:
            raise SystemExit(
                f"{MIP_SPLIT_FILE} [{package}] names modules that no longer "
                f"exist: {', '.join(missing)}"
            )
        if "auto" in names or "__init__" in names:
            raise SystemExit(
                f"{MIP_SPLIT_FILE} [{package}] would move __init__ or auto to the "
                f"host package, which would leave the MCU unable to import {package}"
            )
        host_only[package] = names
    return host_only


def check_no_host_imports(package_dir: Path, host_only: frozenset[str]) -> None:
    """Refuse to ship an MCU module that imports a host-only one at module scope.

    Inside a function is fine and is how every ``auto`` module works; at module
    scope it would make the package unimportable on a board, which is the one
    way this split can break something.
    """
    package = package_dir.name
    pattern = re.compile(
        rf"^(?:from\s+(?:{package}|\.)\s+import\s+(\w+)"
        rf"|from\s+{package}\.(\w+)\s+import"
        rf"|import\s+{package}\.(\w+))"
    )
    for path in sorted(package_dir.glob("*.py")):
        if path.stem in host_only:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line or line[:1].isspace():
                continue
            match = pattern.match(line.strip())
            if match is None:
                continue
            name = next((group for group in match.groups() if group), None)
            if name in host_only:
                raise SystemExit(
                    f"{package}/{path.name}:{lineno} imports the host-only module "
                    f"{name!r} at module scope, so it would not import on a "
                    f"microcontroller. Move the import inside the function, or "
                    f"drop {name!r} from {MIP_SPLIT_FILE}."
                )


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
    # What a microcontroller cannot run does not go on one. Declared in the
    # source repository's mip-split.toml and shipped by pydevices-desktop
    # instead, which already require()s this package -- so a host installs one
    # thing and gets what it always got (pydevices#30).
    host_only = read_host_only(source_root)
    host_components: list[tuple[Path, frozenset[str]]] = []
    for source in sorted(filter(publishable, (source_root / "lib").iterdir()), key=lambda path: path.name):
        names.append(source.stem if source.is_file() else source.name)
        split = host_only.get(source.name, frozenset()) if source.is_dir() else frozenset()
        if not split:
            copy_component(source, package / source.name)
            payloads.append(f'module("{source.name}")' if source.is_file() else f'package("{source.name}")')
            continue
        check_no_host_imports(source, split)
        device_files = sorted(
            path.name for path in source.glob("*.py") if path.stem not in split
        )
        destination = package / source.name
        destination.mkdir(parents=True)
        for name in device_files:
            shutil.copy2(source / name, destination / name)
        # Named file by file rather than as a whole package, so the install
        # list is the manifest and nothing else decides it.
        listed = ", ".join(f'"{name}"' for name in device_files)
        payloads.append(f'package("{source.name}", files=({listed},))')
        host_components.append((source, split))

    if len(names) != len(set(names)):
        raise SystemExit("lib/ contains colliding module and package names")

    (package / "manifest.py").write_text(
        render_pydevices_manifest("pydevices", version, (), tuple(payloads)), encoding="utf-8"
    )

    desktop = destination_root / "pydevices-desktop"
    desktop.mkdir()
    desktop_payloads: list[str] = []
    # The other half of the split: every backend the device package left out.
    for source, split in host_components:
        host_files = sorted(path.name for path in source.glob("*.py") if path.stem in split)
        destination = desktop / source.name
        destination.mkdir(parents=True)
        for name in host_files:
            shutil.copy2(source / name, destination / name)
        listed = ", ".join(f'"{name}"' for name in host_files)
        desktop_payloads.append(f'package("{source.name}", files=({listed},))')
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

    source_repository = args.source_repository.resolve()
    mip_root = args.mip_repository.resolve()
    expected_repository = lockfile_repository(mip_root, args.profile)
    if args.source_repository_name != expected_repository:
        raise SystemExit(
            f"profile {args.profile!r} requires {expected_repository}, "
            f"not {args.source_repository_name}"
        )
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
