"""Tests for scripts/generate_sites.py --only, the path mip's refresh workflow runs."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

PAGE = """<!doctype html>
<html lang="en">
<head>
  <!-- PYDEVICES-HEAD-TAGS: START -->
  <!-- PYDEVICES-HEAD-TAGS: END -->
</head>
<body>
  <!-- PYDEVICES-ABOVE-THE-FOLD: START -->
  <!-- PYDEVICES-ABOVE-THE-FOLD: END -->
    <!-- PYDEVICES-MIP-PACKAGES: START -->
    <!-- PYDEVICES-MIP-PACKAGES: END -->
</body>
</html>
"""


def _package(version: str) -> dict:
    return {
        "name": "pydevices",
        "version": version,
        "description": "Display, input and audio drivers",
        "repository": "PyDevices/pydevices",
        "ref": f"v{version}",
        "release_url": f"https://github.com/PyDevices/pydevices/releases/tag/v{version}",
        "install": 'mip.install("pydevices", index="https://PyDevices.github.io/mip")',
    }


class OnlyMipTests(unittest.TestCase):
    """A workspace holding only dotgithub and mip, as the refresh job lays it out."""

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        dotgithub = self.root / "dotgithub"
        (dotgithub / "scripts").mkdir(parents=True)
        (dotgithub / "data").mkdir()
        shutil.copy2(REPO / "scripts/generate_sites.py", dotgithub / "scripts")
        shutil.copy2(REPO / "data/repos_db.json", dotgithub / "data")
        shutil.copytree(REPO / "assets", dotgithub / "assets")
        self.script = dotgithub / "scripts/generate_sites.py"
        self.mip = self.root / "mip"
        (self.mip / ".site").mkdir(parents=True)
        self.page = self.mip / ".site/index.html"
        self.page.write_text(PAGE, encoding="utf-8")

    def _write_packages(self, version: str) -> None:
        (self.mip / "packages.json").write_text(
            json.dumps({"packages": [_package(version)]}), encoding="utf-8"
        )

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.script), *args],
            capture_output=True, text=True, check=False,
        )

    def test_page_follows_packages_json(self) -> None:
        self._write_packages("0.5.3")
        self.assertEqual(self._run("--only", "mip").returncode, 0)
        self.assertIn("<td>0.5.3</td>", self.page.read_text(encoding="utf-8"))

        self._write_packages("0.5.4")
        result = self._run("--only", "mip")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        page = self.page.read_text(encoding="utf-8")
        self.assertIn("<td>0.5.4</td>", page)
        self.assertIn("releases/tag/v0.5.4", page)
        self.assertNotIn("0.5.3", page)
        self.assertIn("<title>", page)

    def test_rerun_is_byte_identical(self) -> None:
        self._write_packages("0.5.4")
        self._run("--only", "mip")
        first = self.page.read_bytes()
        self._run("--only", "mip")
        self.assertEqual(first, self.page.read_bytes())

    def test_writes_nothing_outside_the_named_repo(self) -> None:
        self._write_packages("0.5.4")
        self.assertEqual(self._run("--only", "mip").returncode, 0)
        self.assertEqual(
            sorted(p.name for p in self.root.iterdir()), ["dotgithub", "mip"]
        )

    def test_missing_page_fails(self) -> None:
        self._write_packages("0.5.4")
        self.page.unlink()
        result = self._run("--only", "mip")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("page not written", result.stderr)

    def test_unknown_repo_fails(self) -> None:
        result = self._run("--only", "no-such-repo")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not in data/repos_db.json", result.stderr)


if __name__ == "__main__":
    unittest.main()
