# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""scripts/style_check.py: each rule fails on a planted fault and passes clean."""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import style_check

HEADER = "# SPDX-FileCopyrightText: 2026 Brad Barnett\n#\n# SPDX-License-Identifier: MIT\n"


class Repo(unittest.TestCase):
    """A scratch tree; ``check`` runs the script over it and returns (code, output)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name
        # Run as a plain local script, whatever environment the tests run in.
        env = mock.patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop("GITHUB_REPOSITORY", None)
        os.environ.pop("GITHUB_ACTIONS", None)

    def write(self, path, text):
        full = os.path.join(self.root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)

    def check(self, *extra):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = style_check.main(["--root", self.root, *extra])
        return code, out.getvalue()


class SpdxRule(Repo):
    def test_clean_file_passes(self):
        self.write("a.py", HEADER + '"""Do a thing."""\n')
        self.assertEqual(self.check()[0], 0)

    def test_any_holder_and_extra_holders_pass(self):
        self.write("a.py", "# SPDX-FileCopyrightText: 2017 Someone Else\n"
                   "# SPDX-FileCopyrightText: 2026 Brad Barnett\n#\n"
                   "# SPDX-License-Identifier: BSD-3-Clause\n")
        self.assertEqual(self.check()[0], 0)

    def test_shebang_and_coding_line_may_come_first(self):
        self.write("a.py", "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n" + HEADER)
        self.assertEqual(self.check()[0], 0)

    def test_missing_header_fails(self):
        self.write("a.py", '"""No header."""\n')
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("a.py:1:", out)

    def test_licence_only_fails(self):
        self.write("a.py", "# SPDX-License-Identifier: MIT\n")
        self.assertEqual(self.check()[0], 1)

    def test_two_line_header_fails(self):
        self.write("a.py", "# SPDX-FileCopyrightText: 2026 Brad Barnett\n"
                   "# SPDX-License-Identifier: MIT\n")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("bare '#'", out)

    def test_header_after_code_fails(self):
        self.write("a.py", "import os\n" + HEADER)
        self.assertEqual(self.check()[0], 1)

    def test_empty_file_passes(self):
        self.write("pkg/__init__.py", "")
        self.assertEqual(self.check()[0], 0)


class DocstringRule(Repo):
    def test_role_in_docstring_fails(self):
        self.write("a.py", HEADER + 'def f():\n    """See :class:`Palette`."""\n')
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("a.py:5:", out)

    def test_prefixed_role_and_ref_and_const_fail(self):
        for role in (":py:func:`f`", ":ref:`page`", ":const:`X`", ":meth:`A.b`", ":mod:`m`"):
            with self.subTest(role=role):
                self.write("a.py", HEADER + f'"""Uses {role}."""\n')
                self.assertEqual(self.check()[0], 1)

    def test_fields_fail(self):
        for field in (":param int x: the x", ":returns: a thing", ":type x: int", ":raises ValueError: no"):
            with self.subTest(field=field):
                self.write("a.py", HEADER + f'"""Do it.\n\n    {field}\n    """\n')
                self.assertEqual(self.check()[0], 1)

    def test_class_and_module_docstrings_checked(self):
        self.write("a.py", HEADER + '"""Mod :mod:`x`."""\nclass C:\n    """:attr:`y`"""\n')
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(out.count("Sphinx role"), 2)

    def test_comments_and_ordinary_strings_are_left_alone(self):
        self.write("a.py", HEADER + '# a :class:`X` in a comment\nT = ":param x: template"\n'
                   'def f():\n    """Plain `Palette` reference."""\n    return T\n')
        self.assertEqual(self.check()[0], 0)

    def test_template_in_a_non_docstring_string_passes(self):
        self.write("a.py", HEADER + '"""Writes docstrings."""\nTEMPLATE = """\n:param x: y\n:class:`Z`\n"""\n')
        self.assertEqual(self.check()[0], 0)

    def test_unparseable_file_is_noted_not_failed(self):
        self.write("a.py", HEADER + "def broken(:\n")
        code, out = self.check()
        self.assertEqual(code, 0)
        self.assertIn("note:", out)


class GithubLinkRule(Repo):
    def test_readme_and_docs_links_fail(self):
        self.write("README.md", "See [the plumbing](https://github.com/PyDevices/.github/blob/main/x.md).\n")
        self.write("docs/guide.md", "![](https://raw.githubusercontent.com/PyDevices/.github/main/a.png)\n")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("README.md:1:", out)
        self.assertIn("docs/guide.md:1:", out)

    def test_other_pydevices_repos_pass(self):
        self.write("README.md", "[pydevices](https://github.com/PyDevices/pydevices) and github.com/PyDevices/.github-x\n")
        self.assertEqual(self.check()[0], 0)

    def test_files_outside_readme_and_docs_are_not_pages(self):
        self.write("CONTRIBUTING.md", "https://github.com/PyDevices/.github\n")
        self.assertEqual(self.check()[0], 0)

    def test_the_dot_github_repo_is_exempt(self):
        self.write("README.md", "https://github.com/PyDevices/.github\n")
        self.assertEqual(self.check("--skip-github-link")[0], 0)
        os.environ["GITHUB_REPOSITORY"] = "PyDevices/.github"
        self.assertEqual(self.check()[0], 0)


class ReadmeRule(Repo):
    def test_badge_row_fails(self):
        for line in (
            "[![CI](https://github.com/PyDevices/x/actions/workflows/ci.yml/badge.svg)](https://x)",
            "![PyPI](https://img.shields.io/pypi/v/x)",
            '<img src="https://img.shields.io/badge/a-b-green">',
        ):
            with self.subTest(line=line):
                self.write("README.md", "# X\n\n" + line + "\n")
                self.assertEqual(self.check()[0], 1)

    def test_lead_image_is_not_a_badge(self):
        self.write("README.md", "![The board](docs/images/board.png)\n\n# X\n")
        self.assertEqual(self.check()[0], 0)

    def test_status_banner_fails(self):
        for line in ("> **Alpha quality.** Expect changes.", "This project is under heavy development.",
                     "Status: beta", "**Status:** experimental"):
            with self.subTest(line=line):
                self.write("README.md", "# X\n\n" + line + "\n")
                self.assertEqual(self.check()[0], 1)

    def test_only_the_root_readme_is_checked_for_banners(self):
        self.write("docs/intro.md", "Alpha quality.\n![](https://img.shields.io/x)\n")
        self.assertEqual(self.check()[0], 0)

    def test_fenced_code_is_skipped(self):
        self.write("README.md", "# X\n\n```\nStatus: ok\n```\n")
        self.assertEqual(self.check()[0], 0)


class ExcludeFile(Repo):
    def setUp(self):
        super().setUp()
        for p in ("vendor/a.py", "vendor/deep/b.py", "src/c.py", "src/tft_x.py", "d.py"):
            self.write(p, "x = 1\n")

    def failing(self):
        _, out = self.check()
        return sorted(line.split(":")[0] for line in out.splitlines() if ":1:" in line)

    def test_no_exclude_file_checks_everything(self):
        self.assertEqual(len(self.failing()), 5)

    def test_directory_glob_and_name_glob(self):
        self.write(style_check.EXCLUDE_FILE, "# third party\nvendor/\nsrc/tft_*.py\n")
        self.assertEqual(self.failing(), ["d.py", "src/c.py"])

    def test_bare_name_matches_anywhere_and_slash_anchors(self):
        self.write(style_check.EXCLUDE_FILE, "b.py\n/d.py\ndeep/c.py\n")
        self.assertEqual(self.failing(), ["src/c.py", "src/tft_x.py", "vendor/a.py"])

    def test_double_star(self):
        self.write(style_check.EXCLUDE_FILE, "**/deep/**\nsrc/**/c.py\n")
        self.assertEqual(self.failing(), ["d.py", "src/tft_x.py", "vendor/a.py"])


class ChangedFilesOnly(Repo):
    def git(self, *args):
        subprocess.run(["git", "-C", self.root, "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                       check=True, capture_output=True)

    def test_base_limits_the_check_to_changed_files(self):
        self.git("init", "-q", "-b", "main")
        self.write("old.py", "x = 1\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "start")
        self.git("checkout", "-qb", "topic")
        self.write("new.py", "y = 2\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "add new")
        code, out = self.check("--base", "main")
        self.assertEqual(code, 1)
        self.assertIn("new.py:1:", out)
        self.assertNotIn("old.py", out)
        self.assertIn("checked 1 files", out)
        self.assertIn("checked 2 files", self.check()[1])


if __name__ == "__main__":
    unittest.main()
