"""Tests for .github/workflows/reusable-prepare-release-pr.yml.

The changelog logic lives inline in the workflow, because the reusable
workflow runs against the *caller's* checkout and has no copy of this
repository's scripts/. So these tests lift the exact heredoc out of the YAML
and run it, rather than a transcription of it that could drift.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PREPARE_WORKFLOW = REPO / ".github/workflows/reusable-prepare-release-pr.yml"

VERSION = "0.5.2"
DATE = "2026-09-22"
HEADING = f"## v{VERSION} ({DATE})"


def changelog_python() -> str:
    """The `python3 - <<'PY'` block from the Write VERSION and CHANGELOG step."""
    text = PREPARE_WORKFLOW.read_text(encoding="utf-8")
    start = text.index("- name: Write VERSION and CHANGELOG")
    block = text[start:]
    begin = block.index("python3 - <<'PY'\n") + len("python3 - <<'PY'\n")
    end = block.index("\n          PY\n", begin)
    return textwrap.dedent(block[begin:end])


def run_changelog_step(
    existing: str | None,
    *,
    bullets: str = "- Second commit\n- First commit\n",
) -> str:
    """Run the workflow's Python over a fixture changelog, return the result."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        script = root / "write_changelog.py"
        script.write_text(changelog_python(), encoding="utf-8")

        changelog = root / "CHANGELOG.md"
        if existing is not None:
            changelog.write_text(existing, encoding="utf-8")

        bullets_file = root / "bullets.md"
        bullets_file.write_text(bullets, encoding="utf-8")

        env = os.environ.copy()
        env.update(
            {
                "V": VERSION,
                "RELEASE_DATE": DATE,
                "CHANGELOG": str(changelog),
                "BULLETS": str(bullets_file),
            }
        )
        subprocess.run(
            [sys.executable, str(script)],
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        return changelog.read_text(encoding="utf-8")


class WriteChangelogTests(unittest.TestCase):
    def test_no_changelog_yet_writes_one_section(self):
        self.assertEqual(
            run_changelog_step(None),
            f"{HEADING}\n\n- Second commit\n- First commit\n",
        )

    def test_unreleased_heading_becomes_the_version(self):
        """The bug in .github#40: the block must not be left stranded."""
        result = run_changelog_step(
            "## Unreleased\n"
            "\n"
            "- A note written between releases\n"
            "\n"
            "## v0.5.1 (2026-09-21)\n"
            "\n"
            "- Something released\n"
        )
        self.assertEqual(
            result,
            f"{HEADING}\n"
            "\n"
            "- A note written between releases\n"
            "\n"
            "- Second commit\n"
            "- First commit\n"
            "\n"
            "## v0.5.1 (2026-09-21)\n"
            "\n"
            "- Something released\n",
        )
        self.assertNotIn("## Unreleased", result)
        # The released history still starts below this release, not above it.
        self.assertLess(result.index(HEADING), result.index("## v0.5.1"))

    def test_unreleased_under_a_title_and_preamble(self):
        """audiocomponents' shape: a `# Changelog` title and prose first."""
        result = run_changelog_step(
            "# Changelog\n"
            "\n"
            "All notable changes are recorded here.\n"
            "\n"
            "## Unreleased\n"
            "\n"
            "### Added\n"
            "\n"
            "- A hand-written note\n"
            "\n"
            "## v0.1.1 (2026-08-01)\n"
        )
        self.assertEqual(
            result,
            "# Changelog\n"
            "\n"
            "All notable changes are recorded here.\n"
            "\n"
            f"{HEADING}\n"
            "\n"
            "### Added\n"
            "\n"
            "- A hand-written note\n"
            "\n"
            "- Second commit\n"
            "- First commit\n"
            "\n"
            "## v0.1.1 (2026-08-01)\n",
        )

    def test_no_unreleased_block_keeps_the_old_behaviour(self):
        result = run_changelog_step(
            "## v0.5.1 (2026-09-21)\n\n- Something released\n"
        )
        self.assertEqual(
            result,
            f"{HEADING}\n"
            "\n"
            "- Second commit\n"
            "- First commit\n"
            "\n"
            "## v0.5.1 (2026-09-21)\n"
            "\n"
            "- Something released\n",
        )

    def test_a_title_keeps_the_release_below_it(self):
        """Without an Unreleased block the section still goes under the title."""
        result = run_changelog_step("# Changelog\n\n## v0.1.0 (2026-01-01)\n")
        self.assertEqual(
            result,
            "# Changelog\n"
            "\n"
            f"{HEADING}\n"
            "\n"
            "- Second commit\n"
            "- First commit\n"
            "\n"
            "## v0.1.0 (2026-01-01)\n",
        )

    def test_empty_unreleased_block_takes_only_the_log(self):
        result = run_changelog_step("## Unreleased\n\n## v0.1.0 (2026-01-01)\n")
        self.assertEqual(
            result,
            f"{HEADING}\n"
            "\n"
            "- Second commit\n"
            "- First commit\n"
            "\n"
            "## v0.1.0 (2026-01-01)\n",
        )

    def test_no_commits_since_the_tag_keeps_the_written_notes(self):
        result = run_changelog_step(
            "## Unreleased\n\n- A note\n\n## v0.1.0 (2026-01-01)\n",
            bullets="",
        )
        self.assertEqual(
            result,
            f"{HEADING}\n"
            "\n"
            "- A note\n"
            "\n"
            "## v0.1.0 (2026-01-01)\n",
        )

    def test_an_unreleased_heading_below_a_release_is_left_alone(self):
        """Only the *first* level-2 heading is the block being released."""
        result = run_changelog_step(
            "## v0.5.1 (2026-09-21)\n\n- Released\n\n## Unreleased\n\n- Orphan\n"
        )
        self.assertTrue(result.startswith(f"{HEADING}\n"))
        self.assertIn("## Unreleased", result)


if __name__ == "__main__":
    unittest.main()
