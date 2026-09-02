#!/usr/bin/env python3
"""Parser contract tests (canonical + QA wrapper). No network."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "skills" / "dev-shared" / "scripts" / "extract_refs.py"
WRAPPER = ROOT / "skills" / "dev-qa-guided-review" / "scripts" / "extract_refs.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ExtractRefsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load(CANONICAL, "extract_refs")

    def test_jira_and_false_positive(self) -> None:
        got = self.mod.extract_all("UTF-8 encoding is fine, real ticket is WEB-42")
        self.assertEqual(got["jira_keys"], ["WEB-42"])

    def test_figma_url(self) -> None:
        got = self.mod.extract_all(
            "see https://www.figma.com/design/AbCd12345/Login?node-id=1-2"
        )
        self.assertEqual(got["figma"][0]["file_key"], "AbCd12345")
        self.assertEqual(got["figma"][0]["node_ids"], ["1:2"])

    def test_gitlab_mr_url_and_bang(self) -> None:
        url = "https://gitlab.example.com/group/app/-/merge_requests/42"
        got = self.mod.extract_all(url)
        self.assertEqual(got["gitlab"]["mrs"][0]["iid"], 42)
        self.assertEqual(got["gitlab"]["project_paths"], ["group/app"])
        bang = self.mod.extract_all("group/sub/app!7")
        self.assertEqual(bang["gitlab"]["mrs"][0]["iid"], 7)

    def test_ssh_remote(self) -> None:
        got = self.mod.extract_gitlab_project_path("git@gitlab.example.com:acme/web.git")
        self.assertEqual(got, "acme/web")

    def test_bare_node_ids(self) -> None:
        got = self.mod.extract_figma_node_ids(
            'Spec node-id=85-1999 and metadata id="203:13054" plus 203:11374'
        )
        self.assertEqual(got, ["85:1999", "203:13054", "203:11374"])

    def test_self_test(self) -> None:
        self.assertEqual(self.mod._run_self_test(), 0)

    def test_wrapper_points_at_canonical(self) -> None:
        text = WRAPPER.read_text(encoding="utf-8")
        self.assertIn("dev-shared", text)
        self.assertIn("runpy", text)
        self.assertTrue(CANONICAL.is_file())


if __name__ == "__main__":
    unittest.main()
