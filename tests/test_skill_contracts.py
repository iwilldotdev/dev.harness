#!/usr/bin/env python3
"""Skill catalog and policy contracts. No network."""

from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
FIX = ROOT / "tests" / "fixtures"


def load_validate_skills():
    path = ROOT / "scripts" / "validate_skills.py"
    spec = importlib.util.spec_from_file_location("validate_skills", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_skill(name: str) -> str:
    return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")


class SkillContractsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.vs = load_validate_skills()

    def test_catalog_validates(self) -> None:
        errors = self.vs.validate(ROOT)
        self.assertEqual(errors, [], msg="\n".join(errors))

    def test_gates_stop(self) -> None:
        for name in (
            "dev-cycle",
            "dev-feature-intake",
            "dev-specify",
            "dev-design",
            "dev-tasks",
            "dev-debug",
            "dev-bug-intake",
            "dev-reproduce-bug",
            "dev-fix-bug",
            "dev-ship",
            "dev-qa-guided-review",
        ):
            text = read_skill(name)
            self.assertTrue(
                "⛔" in text or re.search(r"\bstop\b", text, re.I),
                msg=f"{name} must stop at a gate",
            )
            self.assertRegex(text, r"Gate [0A-Z]")

    def test_router_does_not_implement(self) -> None:
        text = read_skill("dev-cycle")
        self.assertIn("Does **not** plan", text)
        self.assertIn("dev-feature-cycle", text)
        self.assertIn("dev-bug-cycle", text)
        self.assertNotIn("dev-execute", text.split("Do not run specify/execute/debug here")[0])

    def test_bug_cycle_never_enters_specify(self) -> None:
        text = read_skill("dev-bug-cycle")
        self.assertIn("Do **not** use `dev-specify`", text)
        self.assertNotIn("dev-specify` →", text)

    def test_feature_debug_only_on_task_failure(self) -> None:
        text = read_skill("dev-feature-cycle")
        self.assertIn("task-failure", text)
        self.assertNotIn("dev-debug` as a default", text.lower())

    def test_fix_reviews_routes_home(self) -> None:
        text = read_skill("dev-fix-reviews")
        self.assertIn("`dev-execute` (feature)", text)
        self.assertIn("`dev-debug` (hypothesis)", text)
        self.assertIn("`dev-fix-bug` (incomplete patch)", text)

    def test_idempotent_and_untrusted(self) -> None:
        evidence = (
            SKILLS / "dev-shared" / "references" / "evidence-contract.md"
        ).read_text(encoding="utf-8")
        self.assertIn("idempotent", evidence.lower())
        self.assertIn("untrusted", evidence.lower())
        ticket = (FIX / "untrusted-ticket-instruction" / "ticket.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Ignore previous instructions", ticket)
        self.assertIn("prompt injection", evidence.lower())

    def test_missing_screen_is_incomplete(self) -> None:
        design = (FIX / "feature-missing-screen" / "design.md").read_text(encoding="utf-8")
        self.assertIn("INCOMPLETE", design)
        self.assertIn("No screen frame", design)
        self.assertIn("INCOMPLETE", read_skill("dev-design"))

    def test_visual_bug_requires_screen(self) -> None:
        intake = (FIX / "bug-visual" / "intake.md").read_text(encoding="utf-8")
        self.assertIn("203:13054", intake)
        self.assertIn("screen", intake.lower())

    def test_forbidden_write_tool_detected(self) -> None:
        text = (FIX / "forbidden-write-tool" / "SKILL.md").read_text(encoding="utf-8")
        errors = self.vs.write_tool_violations(text, "dev-qa-guided-review")
        self.assertTrue(any("gitlab_save_merge_request" in e for e in errors))
        self.assertTrue(any("gitlab_accept_merge_request" in e for e in errors))

    def test_ship_must_not_accept_mr(self) -> None:
        text = (FIX / "ship-accept-mr" / "SKILL.md").read_text(encoding="utf-8")
        errors = self.vs.write_tool_violations(text, "dev-ship")
        self.assertTrue(any("gitlab_accept_merge_request" in e for e in errors))
        real = read_skill("dev-ship")
        self.assertIn("Never", real)
        self.assertIn("gitlab_accept_merge_request", real)

    def test_secret_scan_flags_receipt_fixture(self) -> None:
        text = (FIX / "secret-in-receipt" / "receipt.md").read_text(encoding="utf-8")
        self.assertRegex(text, self.vs.SECRET)

    def test_no_host_leak_in_published_files(self) -> None:
        for path in list(SKILLS.rglob("*.md")) + list((ROOT / "docs").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(
                self.vs.HOST_LEAK.search(text),
                msg=f"{path} names a specific host",
            )

    def test_conflict_intake_spec_returns_to_origin(self) -> None:
        execute = read_skill("dev-execute")
        self.assertIn("originating gate", execute)
        intake = (FIX / "feature-spec-intake-conflict" / "intake.md").read_text(
            encoding="utf-8"
        )
        spec = (FIX / "feature-spec-intake-conflict" / "spec.md").read_text(encoding="utf-8")
        self.assertIn("SMS", intake)
        self.assertIn("email", spec.lower())


if __name__ == "__main__":
    unittest.main()
