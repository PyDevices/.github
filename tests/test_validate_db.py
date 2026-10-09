"""validate_db() catches database entries that generate nothing anyone serves."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import generate_sites


def _db() -> dict:
    return json.loads((REPO / "data/repos_db.json").read_text(encoding="utf-8"))


class HeroCanvasTests(unittest.TestCase):
    def setUp(self) -> None:
        # The script finds its assets through the workspace layout; a checkout
        # anywhere else (a worktree) still has them beside these tests.
        saved = generate_sites.ASSETS_DIR
        generate_sites.ASSETS_DIR = str(REPO / "assets")
        self.addCleanup(setattr, generate_sites, "ASSETS_DIR", saved)

    def _problems(self, db: dict) -> list[str]:
        try:
            generate_sites.validate_db(db, only="__none__")
        except SystemExit as exc:
            return [line.strip() for line in str(exc).splitlines()]
        return []

    def test_database_has_no_hero_on_a_page_nobody_generates(self) -> None:
        unserved = [
            name for name, data in generate_sites.repos(_db()).items()
            if data.get("hero_canvas") and generate_sites.page_destination(data) == "none"
        ]
        self.assertEqual(unserved, [])

    def test_validator_rejects_a_hero_on_page_none(self) -> None:
        db = copy.deepcopy(_db())
        name = next(n for n, d in generate_sites.repos(db).items() if d.get("hero_canvas"))
        db[name]["page"] = "none"
        problems = self._problems(db)
        self.assertTrue(
            any(p.startswith(f"{name}: hero_canvas") and "page=none" in p for p in problems),
            problems,
        )


if __name__ == "__main__":
    unittest.main()
