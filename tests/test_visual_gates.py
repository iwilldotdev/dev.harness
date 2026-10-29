#!/usr/bin/env python3
"""Visual manifest, pack facts, and epic aggregation. No network."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VisualGatesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        scripts = ROOT / "skills"
        cls.design = load(scripts / "dev-design" / "scripts" / "validate_design.py", "validate_design")
        cls.intake = load(scripts / "dev-shared" / "scripts" / "validate_intake.py", "validate_intake")
        cls.epic = load(scripts / "dev-shared" / "scripts" / "validate_epic.py", "validate_epic")

    def test_design_fact_must_exist_in_the_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            flow = Path(tmp)
            (flow / "figma").mkdir()
            (flow / "figma" / "203-13054.json").write_text(
                json.dumps({"nodes": [{"id": "203:13054", "size": {"width": 480, "height": 320}}]}),
                encoding="utf-8",
            )
            design = flow / "design.md"
            design.write_text(
                "# Design\n\nFigma.\n\n## Visual contract\n\n"
                "| Region | node-id | Facts |\n| --- | --- | --- |\n"
                "| Modal | 203:13054 | 999x111 |\n",
                encoding="utf-8",
            )
            errors = self.design.validate(design)
            self.assertTrue(any("999x111" in error for error in errors))

    def test_visual_bug_intake_requires_the_shared_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            flow = Path(tmp)
            (flow / "intake.md").write_text("Visual bug on screen 203:13054.\n", encoding="utf-8")
            errors = self.intake.validate(flow)
            self.assertTrue(any("visual-manifest.json is required" in error for error in errors))

    def test_epic_blocks_an_incomplete_child(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            child = repo / ".dev" / "features" / "child"
            child.mkdir(parents=True)
            (child / "validation.md").write_text(
                "Verdict: INCOMPLETE\n\n## Completeness\n\n| Item | Status | Evidence | Correction |\n| --- | --- | --- | --- |\n| screen | gap | missing | dev-execute |\n",
                encoding="utf-8",
            )
            epic = repo / ".dev" / "epic.json"
            epic.write_text(
                json.dumps({"schemaVersion": 1, "children": [".dev/features/child"]}),
                encoding="utf-8",
            )
            errors = self.epic.validate(epic, repo)
            self.assertTrue(any("INCOMPLETE" in error for error in errors))
            self.assertTrue(any("open Completeness" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
