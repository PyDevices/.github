# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Each pointer depends on its new name and says where it went."""

import importlib.util
import sys
import tomllib
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_pypi_pointers", REPO / "scripts/build_pypi_pointers.py")
pointers = importlib.util.module_from_spec(spec)
sys.modules["build_pypi_pointers"] = pointers
spec.loader.exec_module(pointers)


class RenderTest(unittest.TestCase):
    def test_every_pointer(self) -> None:
        for old, (version, new, minimum, _imports) in pointers.POINTERS.items():
            with self.subTest(old=old):
                readme, pyproject = pointers.render(old)
                project = tomllib.loads(pyproject)["project"]
                self.assertEqual(project["name"], old)
                self.assertEqual(project["version"], version)
                self.assertEqual(project["dependencies"], [f"{new}>={minimum}"])
                self.assertIn("Development Status :: 7 - Inactive", project["classifiers"])
                self.assertIn(f"https://pypi.org/project/{new}/", readme)
                self.assertIn(f"pip install {new}", readme)


if __name__ == "__main__":
    unittest.main()
