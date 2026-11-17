# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""The omnipython distributions carry type stubs, and the MIP copy doesn't."""

from __future__ import annotations

import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
build = importlib.import_module("build_omnipython_python_distributions")
sync = importlib.import_module("synchronize_mip_package")


def lay_out(root: Path) -> Path:
    lib = root / "lib"
    (lib / "pkg").mkdir(parents=True)
    for name in ("top.py", "top.pyi", "pkg/__init__.py", "pkg/__init__.pyi", "pkg/py.typed"):
        (lib / name).write_text("", encoding="utf-8")
    return lib


class StubsInTheWheel(unittest.TestCase):
    def test_a_top_level_stub_becomes_a_stubs_package(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            lib = lay_out(Path(scratch))
            names = [path.name for path in build.components(lib)]
            self.assertEqual(names, ["pkg", "top.py", "top.pyi"])
            out = Path(scratch) / "src"
            for source in build.components(lib):
                build.copy_component(source, out / source.name)
            shipped = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
            self.assertEqual(
                shipped,
                ["pkg/__init__.py", "pkg/__init__.pyi", "pkg/py.typed", "top-stubs/__init__.pyi", "top.py"],
            )

    def test_the_build_asks_for_a_setuptools_that_includes_stubs(self) -> None:
        text = build.project_text("x", "1.0.0", "d", [], Path("/nonexistent"))
        self.assertIn("setuptools>=69", text)


class StubsInTheDesktopBundle(unittest.TestCase):
    def test_a_bundle_ships_its_stubs_and_marker_though_mip_does_not_list_them(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            package = root / "packages" / "ports"
            (package / "ports").mkdir(parents=True)
            for name in ("__init__.py", "__init__.pyi", "linux.py", "linux.pyi", "py.typed"):
                (package / "ports" / name).write_text("", encoding="utf-8")
            urls = [[f"ports/{name}", f"{build.GITHUB_SELF}packages/ports/ports/{name}"] for name in ("__init__.py", "linux.py")]
            (package / "package.json").write_text(json.dumps({"urls": urls}), encoding="utf-8")
            out = root / "out"
            build.copy_bundle(package, root, out)
            shipped = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
            self.assertEqual(
                shipped,
                ["ports/__init__.py", "ports/__init__.pyi", "ports/linux.py", "ports/linux.pyi", "ports/py.typed"],
            )


class StubsOutOfMip(unittest.TestCase):
    def test_a_package_copied_for_mip_leaves_its_stubs_behind(self) -> None:
        names = ["__init__.py", "__init__.pyi", "py.typed", "__pycache__"]
        self.assertEqual(sync.ignore_debris("lib/pkg", names), {"__init__.pyi", "py.typed", "__pycache__"})


if __name__ == "__main__":
    unittest.main()
