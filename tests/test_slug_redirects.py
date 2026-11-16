# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""A renamed page's old address gets a redirect page, written once."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import generate_sites


class SlugRedirectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db = json.loads((REPO / "data/repos_db.json").read_text(encoding="utf-8"))
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.saved = generate_sites.BASE_DIR
        generate_sites.BASE_DIR = self.tmp.name
        self.addCleanup(setattr, generate_sites, "BASE_DIR", self.saved)

    def test_every_new_slug_is_in_the_database(self) -> None:
        for new in generate_sites.RENAMED_SLUGS.values():
            self.assertIn(new, generate_sites.repos(self.db))

    def test_old_paths_point_at_new_ones_and_a_second_run_changes_nothing(self) -> None:
        self.assertEqual(generate_sites.write_slug_redirects(self.db), len(generate_sites.RENAMED_SLUGS))
        for old, new in generate_sites.RENAMED_SLUGS.items():
            page = Path(self.tmp.name, generate_sites.PORTAL_REPO, old, "index.html").read_text(encoding="utf-8")
            self.assertIn(f'url=/{new}/"', page)
            self.assertIn(f'rel="canonical" href="/{new}/"', page)
        self.assertEqual(generate_sites.write_slug_redirects(self.db), 0)

    def test_old_slugs_are_not_database_keys(self) -> None:
        for old in generate_sites.RENAMED_SLUGS:
            self.assertNotIn(old, generate_sites.repos(self.db))


if __name__ == "__main__":
    unittest.main()
