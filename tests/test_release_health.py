"""Tests for .github/workflows/release-health.yml.

These lift the step's `run:` body out of the YAML and run it against real git
repositories, so what is exercised is the workflow's own text. The case that
matters is .github#34: one release reports several distributions, each
dispatching its own event from a frozen SHA, and the second run's push is
rejected.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HEALTH_WORKFLOW = REPO / ".github/workflows/release-health.yml"


def update_step_shell() -> str:
    """The `run:` body of the fold-and-commit step."""
    text = HEALTH_WORKFLOW.read_text(encoding="utf-8")
    start = text.index("- name: Fold in the report, regenerate the page, and commit")
    block = text[start:]
    begin = block.index("run: |\n") + len("run: |\n")
    return textwrap.dedent(block[begin:])


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def payload(distribution: str, version: str) -> str:
    return json.dumps(
        {
            "distribution": distribution,
            "version": version,
            "run_url": f"https://example.invalid/{distribution}",
            "testpypi": "success",
            "assets": "success",
            "mip": "success",
            "pypi": "skipped",
        }
    )


def run_step(clone: Path, distribution: str, version: str) -> subprocess.CompletedProcess[str]:
    """Run the workflow step in `clone`, as one dispatched report would."""
    script = clone / ".step.sh"
    script.write_text(update_step_shell(), encoding="utf-8")
    runner_temp = clone.parent / f"runner-temp-{distribution}"
    runner_temp.mkdir(exist_ok=True)
    result = subprocess.run(
        ["bash", "-e", ".step.sh"],
        cwd=clone,
        env={
            "PATH": "/usr/bin:/bin",
            "HOME": str(clone.parent),
            "RUNNER_TEMP": str(runner_temp),
            "PAYLOAD": payload(distribution, version),
            "DISTRIBUTION": distribution,
            "RELEASE_VERSION": version,
        },
        capture_output=True,
        text=True,
        check=False,
    )
    script.unlink()
    return result


class ConcurrentReportTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.origin = root / "origin.git"
        subprocess.run(
            ["git", "init", "-q", "--bare", "-b", "main", str(self.origin)],
            check=True,
            capture_output=True,
        )

        seed = root / "seed"
        git(root, "clone", "-q", str(self.origin), str(seed))
        git(seed, "config", "user.email", "test@example.invalid")
        git(seed, "config", "user.name", "Test")
        (seed / "release-health").mkdir()
        (seed / "release-health/data.json").write_text("{}\n", encoding="utf-8")
        (seed / "RELEASE_HEALTH.md").write_text("# Release health\n", encoding="utf-8")
        git(seed, "add", "-A")
        git(seed, "commit", "-q", "-m", "seed")
        git(seed, "push", "-q", "origin", "main")

        # Two checkouts of the same tip: what two reports from one release get,
        # because a repository_dispatch freezes github.sha at creation time.
        self.first = root / "first"
        self.second = root / "second"
        for clone in (self.first, self.second):
            git(root, "clone", "-q", str(self.origin), str(clone))
            git(clone, "config", "user.email", "test@example.invalid")
            git(clone, "config", "user.name", "Test")

    def tearDown(self):
        self._tmp.cleanup()

    def published(self) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "check"
            subprocess.run(
                ["git", "clone", "-q", str(self.origin), str(out)],
                check=True,
                capture_output=True,
            )
            return {
                "data": json.loads((out / "release-health/data.json").read_text()),
                "page": (out / "RELEASE_HEALTH.md").read_text(encoding="utf-8"),
            }

    def test_two_reports_from_one_release_both_land(self):
        """.github#34: the second report must not lose its row to a rejection."""
        first = run_step(self.first, "pydevices-audioinstruments", "0.2.0")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

        second = run_step(self.second, "pydevices-audioeffects", "0.2.0")
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("push rejected (attempt 1)", second.stdout + second.stderr)

        state = self.published()
        self.assertEqual(
            sorted(state["data"]),
            ["pydevices-audioeffects", "pydevices-audioinstruments"],
        )
        self.assertEqual(state["data"]["pydevices-audioeffects"]["version"], "0.2.0")
        self.assertEqual(
            state["data"]["pydevices-audioinstruments"]["version"], "0.2.0"
        )
        # Both rows are on the page, not just the one that pushed first.
        self.assertIn("| [pydevices-audioeffects]", state["page"])
        self.assertIn("| [pydevices-audioinstruments]", state["page"])

    def test_an_uncontended_report_pushes_first_time(self):
        result = run_step(self.first, "pydevices-audiodsp", "0.5.1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("push rejected", result.stdout + result.stderr)
        self.assertEqual(list(self.published()["data"]), ["pydevices-audiodsp"])

    def test_a_repeated_report_is_recorded_not_skipped(self):
        """A re-reported distribution changes its `updated` stamp, so it commits."""
        self.assertEqual(run_step(self.first, "pydevices-cmods", "0.1.0").returncode, 0)
        git(self.first, "pull", "-q", "--ff-only")
        second = run_step(self.first, "pydevices-cmods", "0.1.1")
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(self.published()["data"]["pydevices-cmods"]["version"], "0.1.1")


if __name__ == "__main__":
    unittest.main()
