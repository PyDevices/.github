"""Tests for .github/workflows/reusable-tag-on-release-merge.yml.

The step under test is shell, not Python, so these lift the `run:` block out
of the YAML and run it in a throwaway git repository under the same shell
GitHub uses (`bash -e`). What is tested is the workflow's own text, not a
transcription of it.
"""

from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TAG_WORKFLOW = REPO / ".github/workflows/reusable-tag-on-release-merge.yml"


def detect_step_shell() -> str:
    """The `run:` body of the Detect a VERSION change step."""
    text = TAG_WORKFLOW.read_text(encoding="utf-8")
    start = text.index("- name: Detect a VERSION change")
    block = text[start:]
    begin = block.index("run: |\n") + len("run: |\n")
    end = block.index("\n\n      - name:", begin)
    return textwrap.dedent(block[begin:end])


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


def run_detect(version: str, *, previous: str = "0.1.0") -> subprocess.CompletedProcess:
    """Land `version` in VERSION on top of `previous`, then run the step."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        git(root, "init", "-q", "-b", "main")
        git(root, "config", "user.email", "test@example.invalid")
        git(root, "config", "user.name", "Test")

        (root / "VERSION").write_text(previous + "\n", encoding="utf-8")
        git(root, "add", "VERSION")
        git(root, "commit", "-q", "-m", "first")

        (root / "VERSION").write_text(version + "\n", encoding="utf-8")
        git(root, "add", "VERSION")
        git(root, "commit", "-q", "-m", "release")

        script = root / "detect.sh"
        script.write_text(detect_step_shell(), encoding="utf-8")
        output = root / "github_output"
        output.touch()

        result = subprocess.run(
            ["bash", "-e", str(script)],
            cwd=root,
            env={"PATH": "/usr/bin:/bin", "GITHUB_OUTPUT": str(output)},
            capture_output=True,
            text=True,
            check=False,
        )
        result.github_output = output.read_text(encoding="utf-8")  # type: ignore[attr-defined]
        return result


class RefusedVersionTests(unittest.TestCase):
    """.github#32: a placeholder must not become a tag and a Release."""

    def assert_refused(self, version: str) -> None:
        result = run_detect(version)
        self.assertEqual(result.returncode, 1, f"{version!r} was not refused")
        self.assertIn("refusing to tag", result.stdout + result.stderr)
        self.assertNotIn("changed=true", result.github_output)

    def test_placeholder_is_refused(self):
        self.assert_refused("0.0.0-PLACEHOLDER-BRAD-NAMES-THIS")

    def test_leading_v_is_refused(self):
        self.assert_refused("v0.2.0")

    def test_two_component_version_is_refused(self):
        self.assert_refused("0.2")

    def test_empty_version_is_refused(self):
        self.assert_refused("")

    def test_pep440_illegal_prerelease_is_refused(self):
        self.assert_refused("0.2.0-rc1")


class AcceptedVersionTests(unittest.TestCase):
    def assert_accepted(self, version: str) -> None:
        result = run_detect(version)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("changed=true", result.github_output)
        self.assertIn(f"version={version}", result.github_output)

    def test_release_version(self):
        self.assert_accepted("0.2.0")

    def test_release_candidate(self):
        self.assert_accepted("0.2.0rc1")

    def test_dev_release(self):
        self.assert_accepted("0.2.0.dev1")

    def test_beta_with_multi_digit_components(self):
        self.assert_accepted("1.10.3b2")


class UnchangedVersionTests(unittest.TestCase):
    def test_an_unchanged_version_still_does_nothing(self):
        """The guard must not fire on a commit that did not touch VERSION."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git(root, "init", "-q", "-b", "main")
            git(root, "config", "user.email", "test@example.invalid")
            git(root, "config", "user.name", "Test")
            (root / "VERSION").write_text("0.0.0-PLACEHOLDER\n", encoding="utf-8")
            git(root, "add", "VERSION")
            git(root, "commit", "-q", "-m", "first")
            (root / "README.md").write_text("unrelated\n", encoding="utf-8")
            git(root, "add", "README.md")
            git(root, "commit", "-q", "-m", "second")

            script = root / "detect.sh"
            script.write_text(detect_step_shell(), encoding="utf-8")
            output = root / "github_output"
            output.touch()

            result = subprocess.run(
                ["bash", "-e", str(script)],
                cwd=root,
                env={"PATH": "/usr/bin:/bin", "GITHUB_OUTPUT": str(output)},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("changed=false", output.read_text(encoding="utf-8"))


class ExistingTagTests(unittest.TestCase):
    def test_an_already_tagged_version_is_a_no_op(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git(root, "init", "-q", "-b", "main")
            git(root, "config", "user.email", "test@example.invalid")
            git(root, "config", "user.name", "Test")
            (root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
            git(root, "add", "VERSION")
            git(root, "commit", "-q", "-m", "first")
            (root / "VERSION").write_text("0.2.0\n", encoding="utf-8")
            git(root, "add", "VERSION")
            git(root, "commit", "-q", "-m", "release")
            git(root, "tag", "v0.2.0")

            script = root / "detect.sh"
            script.write_text(detect_step_shell(), encoding="utf-8")
            output = root / "github_output"
            output.touch()

            result = subprocess.run(
                ["bash", "-e", str(script)],
                cwd=root,
                env={"PATH": "/usr/bin:/bin", "GITHUB_OUTPUT": str(output)},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("changed=false", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
