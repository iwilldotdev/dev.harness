#!/usr/bin/env python3
"""Figma pack manifest tests. No network."""

from __future__ import annotations

import base64
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
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FigmaPackTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pack = load(
            ROOT / "skills" / "dev-shared" / "scripts" / "figma_pack.py", "figma_pack"
        )

    def test_manifest_and_cited_screens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            flow = Path(tmp) / "features" / "otp"
            figma = flow / "figma"
            figma.mkdir(parents=True)
            payload = {
                "fileKey": "abc",
                "lastModified": "2026-10-29T10:00:00Z",
                "nodes": [{"id": "203:13054", "name": "Modal", "type": "FRAME"}],
            }
            (figma / "203-13054.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            (figma / "203-13054-shots.png").write_bytes(b"png")  # suffixed naming
            (flow / "design.md").write_text(
                "# Design\n\n## Visual contract\n\n"
                "| Region | node-id | Facts |\n| --- | --- | --- |\n"
                "| Modal | 203:13054 | 480x320 |\n",
                encoding="utf-8",
            )
            cited, missing_json, missing_png = self.pack.build(flow)
            self.assertEqual(cited, ["203:13054"])
            self.assertEqual(missing_json, [])
            self.assertEqual(missing_png, [])
            manifest = json.loads((figma / "pack.json").read_text(encoding="utf-8"))
            entry = manifest["screens"]["abc/203:13054"]
            self.assertEqual(entry["png"], "203-13054-shots.png")
            self.assertEqual(entry["lastModified"], "2026-10-29T10:00:00Z")

    def test_check_fails_when_cited_screen_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            flow = Path(tmp) / "features" / "otp"
            figma = flow / "figma"
            figma.mkdir(parents=True)
            (flow / "design.md").write_text(
                "# Design\n\n## Visual contract\n\n"
                "| Region | node-id | Facts |\n| --- | --- | --- |\n"
                "| Modal | 203:13054 | 480x320 |\n",
                encoding="utf-8",
            )
            cited, missing_json, _ = self.pack.build(flow)
            self.assertEqual(cited, ["203:13054"])
            self.assertEqual(missing_json, ["203:13054"])

    def test_check_rejects_corrupt_png_and_node_mismatch(self) -> None:
        png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        )
        with tempfile.TemporaryDirectory() as tmp:
            flow = Path(tmp) / "flow"
            figma = flow / "figma"
            figma.mkdir(parents=True)
            payload = {
                "schemaVersion": 1,
                "completeness": {"status": "complete", "reasons": []},
                "truncated": False,
                "lastModified": "2026-10-29T10:00:00Z",
                "fileKey": "abc",
                "screenshot": {"format": "png", "scale": 1},
                "warnings": [],
                "nodes": [{"id": "203:13054", "size": {"width": 1, "height": 1}, "characters": "Pay now"}],
            }
            (flow / "design.md").write_text(
                "# Design\n\n## Visual contract\n\n| Region | node-id | Facts |\n| --- | --- | --- |\n| Modal | 203:13054 | 1x1 |\n",
                encoding="utf-8",
            )
            (figma / "203-13054.json").write_text(json.dumps(payload), encoding="utf-8")
            (figma / "203-13054.png").write_bytes(b"not-a-png")
            errors = self.pack.check(flow)
            self.assertTrue(any("not decodable" in error for error in errors))
            (figma / "203-13054.png").write_bytes(png)
            payload["nodes"][0]["id"] = "999:9999"
            (figma / "203-13054.json").write_text(json.dumps(payload), encoding="utf-8")
            errors = self.pack.check(flow)
            self.assertTrue(any("payload node id" in error for error in errors))
            payload["nodes"][0]["id"] = "203:13054"
            payload.pop("schemaVersion")
            (figma / "203-13054.json").write_text(json.dumps(payload), encoding="utf-8")
            errors = self.pack.check(flow)
            self.assertTrue(any("schemaVersion" in error for error in errors))
            payload["schemaVersion"] = 1
            (figma / "203-13054.json").write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(self.pack.check(flow), [])


if __name__ == "__main__":
    unittest.main()
