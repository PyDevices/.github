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


class MovedRepoTests(unittest.TestCase):
    """A repo folded into another one stays a pointer page, off the map and grid."""

    def setUp(self) -> None:
        sys.path.insert(0, str(REPO / "scripts"))
        self.addCleanup(sys.path.remove, str(REPO / "scripts"))
        import generate_sites

        self.gen = generate_sites
        self.db = json.loads((REPO / "data/repos_db.json").read_text(encoding="utf-8"))

    def test_moved_repos_are_named_in_the_map_not_listed_as_products(self) -> None:
        moved = self.db["_meta"]["moved"]
        self.assertTrue(moved)
        block = self.gen.build_ecosystem_markdown(self.db)
        for name in moved:
            self.assertIn(f"- **{name}** \u2014 ", block)
            self.assertNotIn(f"[`{name}`](https://github.com/PyDevices/{name})", block)

    def test_moved_repos_keep_their_page_but_leave_the_grid(self) -> None:
        for name in self.db["_meta"]["moved"]:
            entry = self.db[name]
            self.assertIs(entry.get("portal_grid"), False, name)
            self.assertNotEqual(self.gen.page_destination(entry), "none", name)
            self.assertNotIn(f'href="/{name}/"', self.gen.build_portal_grids_html(self.db))

    def test_the_four_lvgl_repos_give_way_to_omnipython_lvgl(self) -> None:
        moved = self.db["_meta"]["moved"]
        grid = self.gen.build_portal_grids_html(self.db)
        entry = self.db["omnipython-lvgl"]
        self.assertNotEqual(self.gen.page_destination(entry), "none")
        self.assertIn('href="/omnipython-lvgl/"', grid)
        for old in ("lvgl-bindings", "lvgl-micropython", "lvgl-python", "lvgl-circuitpython"):
            self.assertIn(old, moved)
            self.assertNotIn(f'href="/{old}/"', grid)
        block = self.gen.build_ecosystem_markdown(self.db)
        self.assertIn("[`omnipython-lvgl`](https://github.com/PyDevices/omnipython-lvgl)", block)

    def test_audiocomponents_gives_way_to_instruments_and_effects(self) -> None:
        grid = self.gen.build_portal_grids_html(self.db)
        self.assertIn("audiocomponents", self.db["_meta"]["moved"])
        self.assertNotIn('href="/audiocomponents/"', grid)
        for name in ("audioinstruments", "audioeffects"):
            self.assertNotEqual(self.gen.page_destination(self.db[name]), "none", name)
            self.assertIn(f'href="/{name}/"', grid)


if __name__ == "__main__":
    unittest.main()
