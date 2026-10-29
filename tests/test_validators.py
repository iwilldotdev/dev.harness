#!/usr/bin/env python3
"""Deterministic validators against fixtures. No network."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
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
        cls.design = load(
            ROOT / "skills" / "dev-design" / "scripts" / "validate_design.py", "design"
        )
        cls.commit = load(
            ROOT / "skills" / "dev-shared" / "scripts" / "check_commit.py", "commit"
        )
        cls.readiness = load(
            ROOT / "skills" / "dev-shared" / "scripts" / "validate_readiness.py", "readiness"
        )

    def test_feature_happy_path(self) -> None:
        happy = FIX / "feature-happy-path"
        self.assertEqual(self.spec.validate(happy / "spec.md"), [])
        self.assertEqual(self.tasks.validate(happy / "tasks.md"), [])
        self.assertEqual(self.feat.validate(happy / "validation.md"), [])
        self.assertEqual(self.state.validate(happy / "STATE.md"), [])

    def test_feature_pass_with_open_completeness_fails(self) -> None:
        source = (FIX / "feature-happy-path" / "validation.md").read_text(
            encoding="utf-8"
        )
        for status in ("gap", "not-checked"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as tmp:
                validation = Path(tmp) / "validation.md"
                validation.write_text(
                    source.replace("| done |", f"| {status} |", 1),
                    encoding="utf-8",
                )
                errors = self.feat.validate(validation)
                self.assertTrue(any("cannot contain" in e for e in errors))

    def test_missing_ac_fails_spec(self) -> None:
        errors = self.spec.validate(FIX / "feature-missing-ac" / "spec.md")
        self.assertTrue(any("REQ" in e for e in errors))

    def test_bug_reproducible(self) -> None:
        errors = self.bug.validate(FIX / "bug-reproducible")
        self.assertEqual(errors, [])
        self.assertEqual(self.state.validate(FIX / "bug-reproducible" / "STATE.md"), [])

    def test_bug_pass_with_open_completeness_fails(self) -> None:
        source = (FIX / "bug-reproducible" / "validation.md").read_text(
            encoding="utf-8"
        )
        for status in ("gap", "not-checked"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                shutil.copy(FIX / "bug-reproducible" / "intake.md", root / "intake.md")
                shutil.copy(
                    FIX / "bug-reproducible" / "reproduction.md",
                    root / "reproduction.md",
                )
                (root / "validation.md").write_text(
                    source.replace("| done |", f"| {status} |", 1),
                    encoding="utf-8",
                )
                errors = self.bug.validate(root)
                self.assertTrue(any("cannot contain" in e for e in errors))

    def test_bug_not_reproduced_has_no_pass(self) -> None:
        errors = self.bug.validate(FIX / "bug-not-reproduced")
        self.assertTrue(any("missing validation.md" in e for e in errors))
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

    def test_figma_spec_requires_visual_contract(self) -> None:
        path = FIX / "feature-figma-no-contract" / "spec.md"
        errors = self.spec.validate(path)
        self.assertTrue(any("Visual contract" in e for e in errors))
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.md"
            spec.write_text(
                path.read_text(encoding="utf-8") + "\n## Visual contract\n\nScreen 203:13054 width FIXED 320.\n",
                encoding="utf-8",
            )
            self.assertEqual(self.spec.validate(spec), [])
            spec.write_text(
                path.read_text(encoding="utf-8") + "\n## Visual contract\n\nWidth FIXED 320.\n",
                encoding="utf-8",
            )
            errors = self.spec.validate(spec)
            self.assertTrue(any("node-id" in e for e in errors))

    def test_screen_word_alone_does_not_require_visual_contract(self) -> None:
        text = (FIX / "feature-happy-path" / "spec.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.md"
            spec.write_text(text + "\nThe OTP prompt covers the full screen.\n", encoding="utf-8")
            self.assertEqual(self.spec.validate(spec), [])

    def test_design_visual_contract(self) -> None:
        self.assertEqual(self.design.validate(FIX / "feature-visual-design" / "design.md"), [])
        self.assertEqual(self.design.validate(FIX / "feature-missing-screen" / "design.md"), [])
        errors = self.design.validate(FIX / "feature-design-no-contract" / "design.md")
        self.assertTrue(any("Visual contract" in e for e in errors))

    def test_design_contract_must_cite_screen_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "design.md"
            design.write_text(
                "# Design\n\nFigma screen.\n\n## Visual contract\n\n| Region | Facts |\n"
                "| --- | --- |\n| Modal | FIXED 480x320 |\n",
                encoding="utf-8",
            )
            errors = self.design.validate(design)
            self.assertTrue(any("node-id" in e for e in errors))
            design.write_text(
                "# Design\n\nThe login screen keeps its layout.\n\n## Files\n\n- `src/auth.ts`\n",
                encoding="utf-8",
            )
            self.assertEqual(self.design.validate(design), [])

    def test_pass_detection_ignores_prose(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            validation = Path(tmp) / "validation.md"
            validation.write_text(
                "# validation\n\nVerdict: FAIL\n\nPASS requires the lock test; PASSWORD reset untouched.\n\n"
                "## Completeness\n\n| Item | Status | Evidence | Correction |\n"
                "| --- | --- | --- | --- |\n| lock | gap | src/lock.ts:1 | dev-execute |\n",
                encoding="utf-8",
            )
            self.assertEqual(self.feat.validate(validation), [])
            errors = self.feat.validate(validation, require_pass=True)
            self.assertTrue(any("requires verdict PASS" in e for e in errors))

    def test_bug_requires_validation_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "intake.md").write_text("expected: yes\nactual: no\n", encoding="utf-8")
            (root / "reproduction.md").write_text("REPRODUCED\n", encoding="utf-8")
            errors = self.bug.validate(root)
            self.assertTrue(any("missing validation.md" in e for e in errors))
            self.assertTrue(any("requires verdict PASS" in e for e in self.bug.validate(root, require_pass=True)))

    def test_require_pass_accepts_a_real_pass(self) -> None:
        self.assertEqual(
            self.feat.validate(FIX / "feature-happy-path" / "validation.md", require_pass=True),
            [],
        )
        self.assertEqual(self.bug.validate(FIX / "bug-reproducible", require_pass=True), [])

    def test_any_verdict_requires_completeness(self) -> None:
        for verdict in ("FAIL", "INCOMPLETE"):
            with self.subTest(verdict=verdict), tempfile.TemporaryDirectory() as tmp:
                validation = Path(tmp) / "validation.md"
                validation.write_text(f"# validation\n\nVerdict: {verdict}\n", encoding="utf-8")
                errors = self.feat.validate(validation)
                self.assertTrue(any("verdict requires Completeness" in e for e in errors))
                root = Path(tmp) / "bug"
                root.mkdir()
                (root / "intake.md").write_text("expected: yes\nactual: no\n", encoding="utf-8")
                (root / "reproduction.md").write_text("REPRODUCED\n", encoding="utf-8")
                (root / "validation.md").write_text(
                    f"# validation\n\nVerdict: {verdict}\n", encoding="utf-8"
                )
                errors = self.bug.validate(root)
                self.assertTrue(any("verdict requires Completeness" in e for e in errors))

    def test_verdict_line_formats_are_checked(self) -> None:
        table = (
            "\n\n## Completeness\n\n| Item | Status | Evidence | Correction |\n"
            "| --- | --- | --- | --- |\n| REQ-001 | gap | src/a.ts:1 | dev-execute |\n"
        )
        for line in ("**Verdict:** PASS", "**Verdict: PASS**", "## Verdict\n\nPASS (see notes)"):
            with self.subTest(line=line), tempfile.TemporaryDirectory() as tmp:
                validation = Path(tmp) / "validation.md"
                validation.write_text(f"# validation\n\n{line}{table}", encoding="utf-8")
                errors = self.feat.validate(validation)
                self.assertTrue(any("cannot contain" in e for e in errors))
                root = Path(tmp) / "bug"
                root.mkdir()
                (root / "intake.md").write_text("expected: yes\nactual: no\n", encoding="utf-8")
                (root / "reproduction.md").write_text("REPRODUCED\n", encoding="utf-8")
                (root / "validation.md").write_text(f"# validation\n\n{line}{table}", encoding="utf-8")
                errors = self.bug.validate(root)
                self.assertTrue(any("cannot contain" in e for e in errors))

    def test_missing_verdict_line_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            validation = Path(tmp) / "validation.md"
            validation.write_text("# validation\n\nAll good; PASS requires nothing else.\n", encoding="utf-8")
            errors = self.feat.validate(validation)
            self.assertTrue(any("missing verdict line" in e for e in errors))
            root = Path(tmp) / "bug"
            root.mkdir()
            (root / "intake.md").write_text("expected: yes\nactual: no\n", encoding="utf-8")
            (root / "reproduction.md").write_text("REPRODUCED\n", encoding="utf-8")
            (root / "validation.md").write_text("# validation\n\nLooks fine.\n", encoding="utf-8")
            errors = self.bug.validate(root)
            self.assertTrue(any("missing verdict line" in e for e in errors))

    def test_formatted_open_status_is_rejected(self) -> None:
        source = (FIX / "feature-happy-path" / "validation.md").read_text(encoding="utf-8")
        for status in ("`gap`", "**not-checked**"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as tmp:
                validation = Path(tmp) / "validation.md"
                validation.write_text(source.replace("| done |", f"| {status} |", 1), encoding="utf-8")
                errors = self.feat.validate(validation)
                self.assertTrue(any("cannot contain" in e for e in errors))

    def test_readiness_is_bound_to_the_reviewed_commit(self) -> None:
        def git(repo: Path, *args: str) -> str:
            return subprocess.run(
                ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t",
                 "-c", "commit.gpgsign=false", *args],
                check=True, capture_output=True, text=True,
            ).stdout.strip()

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            git(repo, "init", "-q")
            (repo / "app.ts").write_text("export const a = 1;\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-q", "-m", "feat: app")
            sha = git(repo, "rev-parse", "HEAD")
            flow = repo / ".dev" / "features" / "otp"
            (flow / "reviews").mkdir(parents=True)
            receipt = flow / "reviews" / "readiness.md"

            def write(mr: str = "APPROVE", qa_rows: str = "0", qa: bool = True) -> None:
                lines = [f"MR verdict: {mr}", "MR open rows: 0", f"MR reviewed: {sha}"]
                if qa:
                    lines += ["QA verdict: APPROVE", f"QA open rows: {qa_rows}", f"QA reviewed: {sha}"]
                receipt.write_text("\n".join(lines) + "\n", encoding="utf-8")

            write()
            self.assertEqual(self.readiness.validate(flow, repo), [])
            git(repo, "add", ".dev")
            git(repo, "commit", "-q", "-m", "docs: readiness")
            self.assertEqual(self.readiness.validate(flow, repo), [])

            write(mr="ADJUST")
            self.assertTrue(any("ADJUST" in e for e in self.readiness.validate(flow, repo)))
            write(qa_rows="2")
            self.assertTrue(any("open Completeness" in e for e in self.readiness.validate(flow, repo)))
            write(qa=False)
            self.assertTrue(any(e.startswith("QA: needs") for e in self.readiness.validate(flow, repo)))

            write()
            (repo / "new.ts").write_text("export const n = 1;\n", encoding="utf-8")
            errors = self.readiness.validate(flow, repo)
            self.assertTrue(any("untracked files outside .dev" in e for e in errors))
            (repo / "new.ts").unlink()
            (repo / ".dev" / "notes.md").write_text("note\n", encoding="utf-8")
            self.assertEqual(self.readiness.validate(flow, repo), [])
            (repo / ".dev" / "notes.md").unlink()

            write()
            (repo / "app.ts").write_text("export const a = 2;\n", encoding="utf-8")
            errors = self.readiness.validate(flow, repo)
            self.assertTrue(any("changed since the review" in e for e in errors))

    def test_state_rejects_unknown_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "STATE.md"
            state.write_text(
                "flow: feature\ngate: F-A\nbranch: feat/x\nmerge-base: abcdef0\n"
                "artifact: .dev/features/x/intake.md\nnext: dev-specify\nmode: turbo\n",
                encoding="utf-8",
            )
            errors = self.state.validate(state)
            self.assertTrue(any("mode" in e for e in errors))

    def test_design_row_needs_a_concrete_fact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            design = Path(tmp) / "design.md"
            design.write_text(
                "# Design\n\nFigma screen 203:13054.\n\n## Visual contract\n\n"
                "| Region | Screen node-id | Facts |\n| --- | --- | --- |\n"
                "| Modal | 203:13054 | FIXED 480x320, radius 16 |\n"
                "| Button | 203:13060 | follows the design system |\n"
                "| No node | follows the design system |\n",
                encoding="utf-8",
            )
            errors = self.design.validate(design)
            self.assertTrue(any("row 2 needs a concrete fact" in e for e in errors))
            self.assertTrue(any("row 3 must cite the screen node-id" in e for e in errors))
            design.write_text(
                "# Design\n\nFigma screen 203:13054.\n\n## Visual contract\n\n"
                "| Region | Screen node-id | Facts |\n| --- | --- | --- |\n"
                "| Modal | 203:13054 | FIXED 480x320, radius 16 |\n"
                "| Button | 203:13060 | 24x24, copy \"Pay now\" |\n",
                encoding="utf-8",
            )
            self.assertEqual(self.design.validate(design), [])

    def test_spec_ui_section_requires_node_id(self) -> None:
        text = (FIX / "feature-figma-no-contract" / "spec.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.md"
            spec.write_text(
                text + "\n## Visual contract\n\nScreen 203:13054 width FIXED 320.\n",
                encoding="utf-8",
            )
            self.assertEqual(self.spec.validate(spec), [])
            # A second UI REQ section without any node-id must fail.
            spec.write_text(
                text
                + "\n## REQ-002\n\nWhen the shopper opens the drawer, then it shows the cart.\n"
                "Origin: intake.\nExpected outcome: drawer opens.\n"
                "\n## Visual contract\n\nScreen 203:13054 width FIXED 320.\n",
                encoding="utf-8",
            )
            errors = self.spec.validate(spec)
            self.assertTrue(any("must cite the screen node-id" in e for e in errors))

    def test_spec_visual_contract_screens_must_be_covered(self) -> None:
        text = (FIX / "feature-figma-no-contract" / "spec.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.md"
            spec.write_text(
                text
                + "\n## Visual contract\n\n| Region | node-id | Facts |\n| --- | --- | --- |\n"
                "| Modal | 203:13054 | 480x320 |\n| Drawer | 777:12345 | 320x640 |\n",
                encoding="utf-8",
            )
            errors = self.spec.validate(spec)
            self.assertTrue(any("777:12345 is not cited" in e for e in errors))

    def test_tasks_ui_task_requires_node_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tasks = Path(tmp) / "tasks.md"
            tasks.write_text(
                "# Tasks\n\n## Task 1 — Modal\n\n- Files: `src/modal.tsx`\n"
                "- REQ-001\n- Gate: tests pass\n- RED/GREEN\n"
                "- Interfaces: none\n- UI: modal per the design system\n",
                encoding="utf-8",
            )
            errors = self.tasks.validate(tasks)
            self.assertTrue(any("UI task must name the screen node-id" in e for e in errors))
            tasks.write_text(
                "# Tasks\n\n## Task 1 — Modal\n\n- Files: `src/modal.tsx`\n"
                "- REQ-001\n- Gate: tests pass\n- RED/GREEN\n"
                "- Interfaces: none\n- UI (screens): `203:13054` (480x320)\n",
                encoding="utf-8",
            )
            self.assertEqual(self.tasks.validate(tasks), [])
            tasks.write_text(
                "# Tasks\n\n## Task 2 — API\n\n- Files: `src/api.ts`\n"
                "- REQ-002\n- Gate: tests pass\n- RED/GREEN\n"
                "- Interfaces: none\n- UI: sem screen dedicada\n",
                encoding="utf-8",
            )
            self.assertEqual(self.tasks.validate(tasks), [])

    def test_readiness_requires_figma_screens_when_design_has_contract(self) -> None:
        def git(repo: Path, *args: str) -> str:
            return subprocess.run(
                ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t",
                 "-c", "commit.gpgsign=false", *args],
                check=True, capture_output=True, text=True,
            ).stdout.strip()

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            git(repo, "init", "-q")
            (repo / "app.ts").write_text("export const a = 1;\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-q", "-m", "feat: app")
            sha = git(repo, "rev-parse", "HEAD")
            flow = repo / ".dev" / "features" / "otp"
            (flow / "reviews").mkdir(parents=True)
            (flow / "design.md").write_text(
                "# Design\n\n## Visual contract\n\n"
                "| Region | node-id | Facts |\n| --- | --- | --- |\n"
                "| Modal | 203:13054 | 480x320 |\n",
                encoding="utf-8",
            )
            receipt = flow / "reviews" / "readiness.md"
            receipt.write_text(
                f"MR verdict: APPROVE\nMR open rows: 0\nMR reviewed: {sha}\n"
                "QA verdict: APPROVE\nQA open rows: 0\n"
                f"QA reviewed: {sha}\n",
                encoding="utf-8",
            )
            errors = self.readiness.validate(flow, repo)
            self.assertTrue(any("visual-manifest.json is required" in e for e in errors))

            evidence = flow / "evidence" / "visual" / "203-13054" / "default" / "480x320"
            evidence.mkdir(parents=True)
            for name in ("app.png", "figma.png", "diff.png"):
                (evidence / name).write_bytes(b"png")
            entry_id = "REQ-001/203:13054/default/480x320"
            revision = "2026-10-29T10:00:00Z"
            (evidence / "result.json").write_text(
                json.dumps({
                    "schemaVersion": 1,
                    "status": "pass",
                    "entryId": entry_id,
                    "gitSha": sha,
                    "figmaRevision": revision,
                }),
                encoding="utf-8",
            )
            (flow / "visual-manifest.json").write_text(
                json.dumps({
                    "schemaVersion": 1,
                    "unresolved": [],
                    "entries": [{
                        "id": entry_id,
                        "jiraKey": "DEV-1",
                        "requirement": "REQ-001",
                        "fileKey": "abc",
                        "nodeId": "203:13054",
                        "state": "default",
                        "viewport": {"width": 480, "height": 320},
                        "route": "/pay",
                        "figmaRevision": revision,
                        "evidence": "evidence/visual/203-13054/default/480x320/result.json",
                    }],
                }),
                encoding="utf-8",
            )
            receipt.write_text(
                f"MR verdict: APPROVE\nMR open rows: 0\nMR reviewed: {sha}\n"
                "QA verdict: APPROVE\nQA open rows: 0\nQA figma-screens: 2/1\n"
                f"QA reviewed: {sha}\n",
                encoding="utf-8",
            )
            errors = self.readiness.validate(flow, repo)
            self.assertTrue(any("2/1 != calculated 1/1" in e for e in errors))
            receipt.write_text(
                f"MR verdict: APPROVE\nMR open rows: 0\nMR reviewed: {sha}\n"
                "QA verdict: APPROVE\nQA open rows: 0\nQA figma-screens: 1/1\n"
                f"QA reviewed: {sha}\n",
                encoding="utf-8",
            )
            self.assertEqual(self.readiness.validate(flow, repo), [])

    def test_readiness_without_design_skips_figma_screens(self) -> None:
        def git(repo: Path, *args: str) -> str:
            return subprocess.run(
                ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t",
                 "-c", "commit.gpgsign=false", *args],
                check=True, capture_output=True, text=True,
            ).stdout.strip()

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            git(repo, "init", "-q")
            (repo / "app.ts").write_text("export const a = 1;\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-q", "-m", "feat: app")
            sha = git(repo, "rev-parse", "HEAD")
            flow = repo / ".dev" / "features" / "otp"
            (flow / "reviews").mkdir(parents=True)
            (flow / "reviews" / "readiness.md").write_text(
                f"MR verdict: APPROVE\nMR open rows: 0\nMR reviewed: {sha}\n"
                "QA verdict: APPROVE\nQA open rows: 0\n"
                f"QA reviewed: {sha}\n",
                encoding="utf-8",
            )
            self.assertEqual(self.readiness.validate(flow, repo), [])


if __name__ == "__main__":
    unittest.main()
