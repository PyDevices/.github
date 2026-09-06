#!/usr/bin/env python3
"""Tests for scripts/synchronize_mip_package.py."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
SYNC_SCRIPT = SCRIPTS / "synchronize_mip_package.py"


def _load_sync():
    sys.path.insert(0, str(SCRIPTS))
    return importlib.import_module("synchronize_mip_package")


sync = _load_sync()


def write_lockfile(mip: Path, mapping: dict[str, str]) -> None:
    mip.mkdir(parents=True, exist_ok=True)
    payload = {
        profile: {"repository": repository, "ref": "v0.2.0"}
        for profile, repository in mapping.items()
    }
    (mip / "pydevices-lock.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_lib_package(source: Path, package: str) -> None:
    pkg = source / "lib" / package
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text(f"# {package}\n", encoding="utf-8")


def run_sync(
    source: Path,
    mip: Path,
    *,
    source_name: str,
    profile: str,
    version: str = "0.2.0",
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SYNC_SCRIPT),
            "--source-repository",
            str(source),
            "--source-repository-name",
            source_name,
            "--mip-repository",
            str(mip),
            "--profile",
            profile,
            "--version",
            version,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


class LockfileRepositoryTests(unittest.TestCase):
    def test_audiocomponents_dispatch_matches_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            mip = root / "mip"
            write_lib_package(source, "audioinstruments")
            write_lockfile(mip, {"audioinstruments": "PyDevices/audiocomponents"})
            result = run_sync(
                source,
                mip,
                source_name="PyDevices/audiocomponents",
                profile="audioinstruments",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = (mip / "micropython" / "audioinstruments" / "manifest.py").read_text(
                encoding="utf-8"
            )
            self.assertIn('package("audioinstruments")', manifest)
            self.assertTrue(
                (mip / "micropython" / "audioinstruments" / "audioinstruments" / "__init__.py").is_file()
            )

    def test_audioeffects_dispatch_matches_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            mip = root / "mip"
            write_lib_package(source, "audioeffects")
            write_lockfile(mip, {"audioeffects": "PyDevices/audiocomponents"})
            result = run_sync(
                source,
                mip,
                source_name="PyDevices/audiocomponents",
                profile="audioeffects",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((mip / "micropython" / "audioeffects" / "manifest.py").is_file())

    def test_stale_audioif_caller_is_rejected_when_lockfile_names_audiocomponents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            mip = root / "mip"
            write_lib_package(source, "audioinstruments")
            write_lockfile(mip, {"audioinstruments": "PyDevices/audiocomponents"})
            result = run_sync(
                source,
                mip,
                source_name="PyDevices/audioif",
                profile="audioinstruments",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "profile 'audioinstruments' requires PyDevices/audiocomponents, not PyDevices/audioif",
                result.stderr,
            )

    def test_profile_missing_from_lockfile_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            mip = root / "mip"
            write_lib_package(source, "audioinstruments")
            write_lockfile(mip, {"palettes": "PyDevices/palettes"})
            result = run_sync(
                source,
                mip,
                source_name="PyDevices/audiocomponents",
                profile="audioinstruments",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("is not in", result.stderr)
            self.assertIn("add it before publishing", result.stderr)

    def test_missing_lockfile_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            mip = root / "mip"
            mip.mkdir()
            write_lib_package(source, "audioinstruments")
            result = run_sync(
                source,
                mip,
                source_name="PyDevices/audiocomponents",
                profile="audioinstruments",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("pydevices-lock.json", result.stderr)
            self.assertIn("audioinstruments", result.stderr)

    def test_no_hardcoded_profile_repositories_map(self) -> None:
        self.assertFalse(hasattr(sync, "PROFILE_REPOSITORIES"))

    def test_lockfile_repository_reads_named_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mip = Path(tmp)
            write_lockfile(
                mip,
                {
                    "audioinstruments": "PyDevices/audiocomponents",
                    "pydevices": "PyDevices/pydevices",
                },
            )
            self.assertEqual(
                sync.lockfile_repository(mip, "audioinstruments"),
                "PyDevices/audiocomponents",
            )


if __name__ == "__main__":
    unittest.main()
