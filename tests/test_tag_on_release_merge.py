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


def manual_step_shell() -> str:
    """The `run:` body of the Resolve a manual release step."""
    text = TAG_WORKFLOW.read_text(encoding="utf-8")
    start = text.index("- name: Resolve a manual release")
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
        self.assert_refused("0.0.0-PLACEHOLDER-MAINTAINER-NAMES-THIS")

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


class ManualReleaseTests(unittest.TestCase):
    """The workflow_dispatch path: recovery for a merge event GitHub lost."""

    def run_manual(self, history, release="", *, dry_run="false",
                   ref="refs/heads/main", tags=(), setup=None):
        """`history` is a list of VERSION contents, one commit each (None means
        a commit that leaves VERSION alone). Returns (result, shas)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git(root, "init", "-q", "-b", "main")
            git(root, "config", "user.email", "test@example.invalid")
            git(root, "config", "user.name", "Test")
            shas = []
            for number, version in enumerate(history):
                if version is None:
                    (root / "other.txt").write_text(f"{number}\n", encoding="utf-8")
                    git(root, "add", "other.txt")
                else:
                    (root / "VERSION").write_text(version + "\n", encoding="utf-8")
                    git(root, "add", "VERSION")
                git(root, "commit", "-q", "-m", f"commit {number}")
                shas.append(subprocess.run(
                    ["git", "-C", str(root), "rev-parse", "HEAD"],
                    check=True, capture_output=True, text=True).stdout.strip())
            for tag in tags:
                git(root, "tag", tag)
            if setup:
                setup(root, shas)
            script = root / "manual.sh"
            script.write_text(manual_step_shell(), encoding="utf-8")
            output = root / "github_output"
            output.touch()
            release = release(shas) if callable(release) else release
            result = subprocess.run(
                ["bash", "-e", str(script)],
                cwd=root,
                env={"PATH": "/usr/bin:/bin", "GITHUB_OUTPUT": str(output),
                     "GITHUB_REF": ref, "DEFAULT_BRANCH": "main",
                     "RELEASE": release, "DRY_RUN": dry_run},
                capture_output=True, text=True, check=False)
            result.github_output = output.read_text(encoding="utf-8")  # type: ignore[attr-defined]
            return result, shas

    def assert_tags(self, result, version, sha):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("changed=true", result.github_output)
        self.assertIn(f"version={version}", result.github_output)
        self.assertIn(f"sha={sha}", result.github_output)

    def assert_refused(self, result):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("refusing to tag", result.stdout + result.stderr)
        self.assertNotIn("changed=true", result.github_output)

    def test_blank_tags_the_commit_that_set_the_current_version(self):
        result, shas = self.run_manual(["0.1.0", None, "0.2.0", None, None])
        self.assert_tags(result, "0.2.0", shas[2])

    def test_a_named_version_finds_its_own_commit(self):
        result, shas = self.run_manual(
            ["0.1.0", "0.2.0", None, "0.3.0"], release="0.2.0")
        self.assert_tags(result, "0.2.0", shas[1])

    def test_a_run_of_commits_at_one_version_tags_the_first(self):
        result, shas = self.run_manual(["0.1.0", "0.2.0", "0.2.0\n", None])
        self.assert_tags(result, "0.2.0", shas[1])

    def test_a_merge_sha_works(self):
        result, shas = self.run_manual(
            ["0.1.0", "0.2.0", "0.3.0"], release=lambda s: s[1][:10])
        self.assert_tags(result, "0.2.0", shas[1])

    def test_a_sha_that_did_not_set_the_version_is_refused(self):
        result, shas = self.run_manual(
            ["0.1.0", "0.2.0", None, None], release=lambda s: s[3])
        self.assert_refused(result)
        self.assertIn(f"that is {shas[1]}", result.stdout + result.stderr)

    def test_a_placeholder_version_is_refused(self):
        self.assert_refused(self.run_manual(["0.1.0", "0.0.0-PLACEHOLDER"])[0])

    def test_a_named_version_that_was_never_set_is_refused(self):
        self.assert_refused(self.run_manual(["0.1.0", "0.2.0"], release="0.9.0")[0])

    def test_a_version_not_matching_the_grammar_is_refused(self):
        self.assert_refused(self.run_manual(["0.1.0", "0.2.0"], release="v0.2.0")[0])

    def test_a_sha_whose_version_is_a_placeholder_is_refused(self):
        result, _ = self.run_manual(
            ["0.1.0", "junk", "0.2.0"], release=lambda s: s[1])
        self.assert_refused(result)

    def test_an_unknown_sha_is_refused(self):
        self.assert_refused(
            self.run_manual(["0.1.0", "0.2.0"], release="deadbeef")[0])

    def test_a_sha_off_the_default_branch_is_refused(self):
        def branch(root, shas):
            git(root, "checkout", "-q", "-b", "side", shas[0])
            (root / "VERSION").write_text("0.9.0\n", encoding="utf-8")
            git(root, "commit", "-q", "-am", "side")
            side = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                                  check=True, capture_output=True, text=True).stdout.strip()
            git(root, "checkout", "-q", "main")
            shas.append(side)
        result, _ = self.run_manual(
            ["0.1.0", "0.2.0"], release=lambda s: s[2], setup=branch)
        self.assert_refused(result)

    def test_a_branch_other_than_the_default_is_refused(self):
        result, _ = self.run_manual(["0.1.0", "0.2.0"], ref="refs/heads/feature")
        self.assert_refused(result)

    def test_an_existing_tag_is_a_no_op(self):
        result, _ = self.run_manual(["0.1.0", "0.2.0"], tags=["v0.2.0"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("changed=false", result.github_output)
        self.assertNotIn("changed=true", result.github_output)

    def test_a_dry_run_says_what_it_would_tag_and_tags_nothing(self):
        result, shas = self.run_manual(["0.1.0", "0.2.0"], dry_run="true")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"would tag v0.2.0 at {shas[1]}", result.stdout)
        self.assertNotIn("changed=true", result.github_output)


class WorkflowShapeTests(unittest.TestCase):
    def test_the_push_path_is_not_taken_on_a_manual_run(self):
        text = TAG_WORKFLOW.read_text(encoding="utf-8")
        detect = text[text.index("- name: Detect a VERSION change"):]
        self.assertIn("if: github.event_name != 'workflow_dispatch'",
                      detect[:detect.index("run:")])

    def test_inputs_are_optional_so_existing_callers_keep_working(self):
        text = TAG_WORKFLOW.read_text(encoding="utf-8")
        inputs = text[text.index("workflow_call:"):text.index("permissions:")]
        self.assertEqual(inputs.count("required: false"), 2)
        self.assertNotIn("required: true", inputs)


if __name__ == "__main__":
    unittest.main()
