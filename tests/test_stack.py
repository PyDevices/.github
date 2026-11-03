"""The stack check fails on what it exists to catch."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("stack", REPO / "scripts/stack.py")
stack = importlib.util.module_from_spec(spec)
sys.modules["stack"] = stack
spec.loader.exec_module(stack)


def _data() -> dict:
    return {
        "groups": [{"id": "a", "title": "Do a thing, well", "want": "do a thing"}],
        "get": {"clone": "from source"},
        "scan": [{"repo": "one", "glob": "lib/*"}],
        "not_listed": {"one:lib/skip.py": "not for users"},
        "repos_not_listed": {"workspace": "private"},
        "entries": [{
            "name": "thing", "group": "a", "does": "Do it.", "repo": "one",
            "path": "lib/thing.py", "get": ["mip:thing", "clone"], "runs": "MP",
        }],
    }


class StackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.lib = self.root / "one/lib"
        self.lib.mkdir(parents=True)
        (self.lib / "thing.py").write_text("")
        (self.lib / "skip.py").write_text("")
        (self.root / "pydevices/drivers").mkdir(parents=True)
        (self.root / "pydevices/board_configs/desktop").mkdir(parents=True)
        (self.root / "pydevices/drivers/drivers.toml").write_text('[gt911]\nversion = "1"\n')

    def test_a_listed_tree_passes(self) -> None:
        self.assertEqual(stack.check_tree(_data(), str(self.root)), [])

    def test_a_new_module_without_a_row_fails(self) -> None:
        (self.lib / "new.py").write_text("")
        self.assertEqual(stack.check_tree(_data(), str(self.root)),
                         ["one:lib/new.py has no row in data/stack.json"])

    def test_a_new_package_folder_without_a_row_fails(self) -> None:
        (self.lib / "newpkg").mkdir()
        (self.lib / "newpkg/__init__.py").write_text("")
        self.assertIn("one:lib/newpkg has no row in data/stack.json",
                      stack.check_tree(_data(), str(self.root)))

    def test_what_a_removed_package_leaves_behind_is_not_a_module(self) -> None:
        (self.lib / "gone/.ruff_cache").mkdir(parents=True)
        (self.lib / "gone/__pycache__").mkdir()
        self.assertEqual(stack.check_tree(_data(), str(self.root)), [])

    def test_a_removed_module_fails(self) -> None:
        (self.lib / "thing.py").unlink()
        self.assertEqual(stack.check_tree(_data(), str(self.root)),
                         ["thing: one/lib/thing.py is gone"])

    def test_a_dead_guide_fails(self) -> None:
        data = _data()
        data["entries"][0]["guide"] = "docs/thing.md"
        self.assertEqual(stack.check_tree(data, str(self.root)),
                         ["thing: guide one/docs/thing.md is gone"])

    def test_the_index_and_the_rows_must_agree(self) -> None:
        index = {"packages": [{"name": "gt911"}, {"name": "desktop"}, {"name": "stray"}]}
        self.assertEqual(stack.check_index(_data(), str(self.root), index), [
            "thing: mip package is not in the index",
            "stray: in the mip index with no row in data/stack.json",
        ])

    def test_a_new_public_repository_fails(self) -> None:
        repos = [{"name": "one", "isArchived": False}, {"name": "workspace", "isArchived": False},
                 {"name": "old", "isArchived": True}, {"name": "new", "isArchived": False}]
        self.assertEqual(stack.check_repos(_data(), repos),
                         ["new: public repository with no row in data/stack.json"])

    def test_the_page_links_headings_by_the_anchors_they_get(self) -> None:
        block = stack.build_block(_data())
        self.assertIn("(#do-a-thing-well)", block)
        self.assertIn("## Do a thing, well", block)
        self.assertIn("`mip thing`, from source", block)

    def test_text_outside_the_markers_survives(self) -> None:
        page = f"# Title\n\n{stack.START}\nold\n{stack.END}\n\nFooter\n"
        out = stack.page_with_block(page, "new")
        self.assertEqual(out, "# Title\n\nnew\n\nFooter\n")

    def test_the_real_data_is_well_formed(self) -> None:
        data = json.loads((REPO / "data/stack.json").read_text(encoding="utf-8"))
        ids = {g["id"] for g in data["groups"]}
        self.assertTrue(all(e["group"] in ids for e in data["entries"]))


if __name__ == "__main__":
    unittest.main()
