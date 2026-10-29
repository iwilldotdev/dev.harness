#!/usr/bin/env python3
"""Fail an epic ship when any UI child is GAP, FAIL, INCOMPLETE, or BLOCK. No network."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

CONTRACT_PATH = Path(__file__).with_name("visual_contract.py")
VERDICT_LINE = re.compile(r"(?:(?i:verdict)\s*:?\s*)?(PASS|FAIL|INCOMPLETE|BLOCK)(?=\s*(?:$|[—–:.,;(-]))")
OPEN_ROW = re.compile(r"^\|[^|\n]+\|\s*[`*_]*\s*(gap|not-checked)\s*[`*_]*\s*\|", re.I | re.M)


def load_contract():
    spec = importlib.util.spec_from_file_location("visual_contract", CONTRACT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(CONTRACT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRACT = load_contract()


def verdict_of(text: str) -> str | None:
    for line in text.splitlines():
        plain = re.sub(r"^[\s#>-]+", "", re.sub(r"[*_`]", "", line))
        match = VERDICT_LINE.match(plain)
        if match:
            return match.group(1)
    return None


def validate(epic_path: Path, repo: Path) -> list[str]:
    if not epic_path.is_file():
        return [f"missing {epic_path}"]
    try:
        payload = json.loads(epic_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        return [f"epic manifest: {err}"]
    if payload.get("schemaVersion") != 1 or not isinstance(payload.get("children"), list):
        return ["epic manifest requires schemaVersion 1 and children"]
    errors: list[str] = []
    for child in payload["children"]:
        flow = (repo / str(child)).resolve() if not Path(str(child)).is_absolute() else Path(str(child))
        if not flow.is_dir():
            errors.append(f"{child}: flow directory missing")
            continue
        validation = flow / "validation.md"
        if not validation.is_file():
            errors.append(f"{child}: missing validation.md")
            continue
        text = validation.read_text(encoding="utf-8")
        verdict = verdict_of(text)
        if verdict != "PASS":
            errors.append(f"{child}: verdict {verdict or 'missing'} blocks the epic")
        if OPEN_ROW.search(text):
            errors.append(f"{child}: open Completeness row blocks the epic")
        if (flow / "visual-manifest.json").is_file() or CONTRACT.cited_from_flow(flow):
            visual = CONTRACT.evidence_errors(flow, set())
            blocking = [
                item
                for item in visual
                if "figma-screens" not in item and "reviewed commit" not in item
            ]
            errors.extend(f"{child}: {item}" for item in blocking)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("epic_manifest", help=".dev/epic.json")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args(argv)
    errors = validate(Path(args.epic_manifest), Path(args.repo))
    if errors:
        print("FAIL")
        for error in errors:
            print(error)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
