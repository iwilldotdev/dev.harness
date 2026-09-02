#!/usr/bin/env python3
"""Deterministic validators against fixtures. No network."""

from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ValidatorsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = load(
            ROOT / "skills" / "dev-specify" / "scripts" / "validate_spec.py", "spec"
        )
        cls.tasks = load(
            ROOT / "skills" / "dev-tasks" / "scripts" / "validate_tasks.py", "tasks"
        )
        cls.feat = load(
            ROOT / "skills" / "dev-verify-feature" / "scripts" / "validate_feature.py",
            "feat",
        )
        cls.bug = load(
            ROOT / "skills" / "dev-verify-bug" / "scripts" / "validate_bug.py", "bug"
        )
        cls.state = load(
            ROOT / "skills" / "dev-shared" / "scripts" / "validate_state.py", "state"
        )
        cls.commit = load(
            ROOT / "skills" / "dev-shared" / "scripts" / "check_commit.py", "commit"
        )

    def test_feature_happy_path(self) -> None:
        happy = FIX / "feature-happy-path"
        self.assertEqual(self.spec.validate(happy / "spec.md"), [])
        self.assertEqual(self.tasks.validate(happy / "tasks.md"), [])
        self.assertEqual(self.feat.validate(happy / "validation.md"), [])
        self.assertEqual(self.state.validate(happy / "STATE.md"), [])

    def test_missing_ac_fails_spec(self) -> None:
        errors = self.spec.validate(FIX / "feature-missing-ac" / "spec.md")
        self.assertTrue(any("REQ" in e for e in errors))

    def test_bug_reproducible(self) -> None:
        errors = self.bug.validate(FIX / "bug-reproducible")
        self.assertEqual(errors, [])
        self.assertEqual(self.state.validate(FIX / "bug-reproducible" / "STATE.md"), [])

    def test_bug_not_reproduced_has_no_pass(self) -> None:
        errors = self.bug.validate(FIX / "bug-not-reproduced")
        self.assertEqual(errors, [])
        repro = (FIX / "bug-not-reproduced" / "reproduction.md").read_text(encoding="utf-8")
        self.assertIn("NOT REPRODUCED", repro)
        self.assertIn("INCONCLUSIVE", repro)

    def test_hypothesis_without_falsification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copy(FIX / "bug-reproducible" / "intake.md", root / "intake.md")
            shutil.copy(FIX / "bug-reproducible" / "reproduction.md", root / "reproduction.md")
            shutil.copy(
                FIX / "bug-hypothesis-no-evidence" / "hypothesis.md",
                root / "hypothesis.md",
            )
            errors = self.bug.validate(root)
            self.assertTrue(any("falsifiable" in e for e in errors))

    def test_pass_without_red_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copy(FIX / "bug-reproducible" / "intake.md", root / "intake.md")
            shutil.copy(FIX / "bug-reproducible" / "reproduction.md", root / "reproduction.md")
            shutil.copy(FIX / "bug-test-not-red" / "validation.md", root / "validation.md")
            errors = self.bug.validate(root)
            self.assertTrue(any("RED" in e for e in errors))

    def test_commit_rejects_attribution_trailer(self) -> None:
        errors = self.commit.check("feat: add otp\n\nCo-authored-by: Agent <a@b.c>\n")
        self.assertTrue(errors)
        self.assertEqual(self.commit.check("feat: add otp"), [])


if __name__ == "__main__":
    unittest.main()
