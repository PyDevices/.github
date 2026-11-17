#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Build the last release of each retired PyPI name, which installs its new name.

Each pointer is an empty package one patch above the old name's last release.
It depends on the new name and its README says where the package went, so an
old ``pip install`` line keeps working and pulls in the current package.

Run ``python3 scripts/build_pypi_pointers.py --out-dir dist`` with ``build``
installed. The publish-pypi-pointers workflow runs it and uploads the result.
"""
import argparse
import pathlib
import subprocess
import sys
import tempfile

# Old name: (pointer version, new name, lowest new version, how imports change).
POINTERS = {
    "pydevices": (
        "0.3.8", "omnipython", "0.8.0",
        "Your imports keep their names: `displaydev`, `events`, `multimer` and the rest.",
    ),
    "pydevices-desktop": (
        "0.3.8", "omnipython-desktop", "0.8.0",
        "Your imports keep their names, such as `board_config` and `usdl2`.",
    ),
    "pydevices-audiodsp": (
        "0.6.11", "omnipython-audiodsp", "0.6.16",
        "Your imports keep their names: `audiocore`, `audiomixer` and the rest.",
    ),
    "pydevices-audioif": (
        "0.0.5", "omnipython-audiodsp", "0.6.16",
        "Your imports keep their names: `audiocore`, `audiomixer` and the rest. "
        "The instruments and effects it also carried are now "
        "`omnipython-audioinstruments` and `omnipython-audioeffects`: install those too.",
    ),
    "pydevices-lvgl": (
        "9.5.38", "omnipython-lvgl", "9.6.1",
        "You still `import lvgl`.",
    ),
    "pydevices-pygraphics": (
        "0.0.38", "omnipython-pygraphics", "0.2.0",
        "You still `import pygraphics`.",
    ),
    "pydevices-palettes": (
        "0.0.13", "omnipython-palettes", "0.1.0",
        "You still `import palettes`.",
    ),
    "pydevices-pdwidgets": (
        "0.0.23", "omnipython-pdwidgets", "0.0.26",
        "You still `import pdwidgets`.",
    ),
    "pydevices-mpftp": (
        "0.0.4", "mcuctl", "0.2.0",
        "The `mpftp` command is now `mcuctl`, the command-line tool for MicroPython and CircuitPython boards.",
    ),
}

README = """# {old}

{old} has moved to [{new}](https://pypi.org/project/{new}/). Install that instead: `pip install {new}`. {imports}

This last release of {old} contains no code. It only installs {new}, so an old install line keeps working.
"""

PYPROJECT = """[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "{old}"
version = "{version}"
description = "{old} has moved to {new}"
readme = "README.md"
license = "MIT"
requires-python = ">=3.9"
dependencies = ["{new}>={minimum}"]
classifiers = ["Development Status :: 7 - Inactive"]

[project.urls]
"New package" = "https://pypi.org/project/{new}/"

[tool.setuptools]
packages = []
"""


def render(old: str) -> tuple[str, str]:
    """Return the README and pyproject.toml text for one retired name.

    Args:
        old: A key of `POINTERS`.
    """
    version, new, minimum, imports = POINTERS[old]
    fields = {"old": old, "version": version, "new": new, "minimum": minimum, "imports": imports}
    return README.format(**fields), PYPROJECT.format(**fields)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out-dir", required=True, type=pathlib.Path)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        for old in POINTERS:
            project = pathlib.Path(work) / old
            project.mkdir()
            readme, pyproject = render(old)
            (project / "README.md").write_text(readme)
            (project / "pyproject.toml").write_text(pyproject)
            subprocess.run(
                [sys.executable, "-m", "build", "--outdir", str(args.out_dir.resolve()), str(project)],
                check=True,
            )
    for path in sorted(args.out_dir.iterdir()):
        print(path.name)


if __name__ == "__main__":
    main()
