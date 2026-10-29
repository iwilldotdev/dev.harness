#!/usr/bin/env python3
"""Validate feature design.md visual contract. No network."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path

CONTRACT_PATH = Path(__file__).resolve().parents[2] / "dev-shared" / "scripts" / "visual_contract.py"

PLACEHOLDERS = ("TODO", "TBD", "add validation")
UI_REF = re.compile(r"(figma|node-id)", re.I)
INCOMPLETE = re.compile(r"visual design\s*[:=]\s*INCOMPLETE", re.I)
VISUAL = re.compile(r"^## Visual contract\b[^\n]*\n(.*?)(?=^## |\Z)", re.M | re.S)
NODE_ID = re.compile(r"\b\d+[:-]\d+\b")
# Concrete fact: a dimension (480x320 / 265px), a hex color, or a quoted literal copy.
FACT = re.compile(
    r"(\d+(?:\.\d+)?\s*(?:×|x)\s*\d+|\d+px|#[0-9a-fA-F]{3,8}|\"[^\"]{1,200}\"|“[^”]{1,200}”)"
)

ROW = re.compile(r"^\|(.+)\|\s*$", re.M)
SEPARATOR_ROW = re.compile(r"^\|[\s:|-]+\|?\s*$")


def visual_contract_rows(section: str) -> list[list[str]]:
    candidates: list[list[str]] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or SEPARATOR_ROW.match(stripped):
            continue
        candidates.append([cell.strip() for cell in stripped.strip("|").split("|")])
    if not candidates:
        return []
    # The first row is the table header (Region | node-id | Facts…); every
    # following row is a screen region and must carry node-id + facts.
    return candidates[1:]


def load_contract():
    spec = importlib.util.spec_from_file_location("visual_contract", CONTRACT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(CONTRACT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRACT = load_contract()


def pack_value_errors(design_path: Path, section: str) -> list[str]:
    flow = design_path.parent
    figma = flow / "figma"
    manifest_path = flow / "visual-manifest.json"
    if not figma.is_dir() and not manifest_path.is_file():
        return []
    errors: list[str] = []
    if manifest_path.is_file():
        manifest, err = CONTRACT.load_json(manifest_path)
        if manifest is None:
            errors.append(f"visual-manifest.json: {err}")
        else:
            errors.extend(CONTRACT.manifest_errors(manifest))
            covered = {
                str(entry.get("nodeId"))
                for entry in (manifest or {}).get("entries") or []
                if isinstance(entry, dict)
            }
            for node_id in CONTRACT.cited_ids(design_path.read_text(encoding="utf-8")):
                if node_id not in covered:
                    errors.append(f"visual manifest does not cover {node_id}")
    for index, cells in enumerate(visual_contract_rows(section), start=1):
        row = " | ".join(cells)
        node_ids = [f"{match.group(1)}:{match.group(2)}" for match in CONTRACT.NODE_ID.finditer(row)]
        facts = FACT.findall(row)
        if not node_ids or not facts or not figma.is_dir():
            continue
        for node_id in node_ids:
            payload_path = figma / f"{node_id.replace(':', '-')}.json"
            if not payload_path.is_file():
                errors.append(f"Visual contract row {index} has no pack JSON for {node_id}")
                continue
            try:
                blob = payload_path.read_text(encoding="utf-8")
                json.loads(blob)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as err:
                errors.append(f"Visual contract row {index} pack JSON is unreadable: {err}")
                continue
            for fact in facts:
                if fact not in blob and fact.strip("\"“”") not in blob:
                    errors.append(f"Visual contract row {index} fact {fact} is not in the pack for {node_id}")
    return errors


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing {path}"]
    text = path.read_text(encoding="utf-8")
    for token in PLACEHOLDERS:
        if token.lower() in text.lower():
            errors.append(f"placeholder {token}")
    if not UI_REF.search(text):
        return errors
    visual = VISUAL.search(text)
    if visual:
        if not NODE_ID.search(visual.group(1)):
            errors.append("Visual contract must cite the screen node-id")
        for index, cells in enumerate(visual_contract_rows(visual.group(1)), start=1):
            row = " | ".join(cells)
            if not NODE_ID.search(row):
                errors.append(f"Visual contract row {index} must cite the screen node-id")
                continue
            if not FACT.search(row):
                errors.append(
                    f"Visual contract row {index} needs a concrete fact "
                    "(measure, hex color, or literal copy)"
                )
        errors.extend(pack_value_errors(path, visual.group(1)))
    elif not INCOMPLETE.search(text):
        errors.append("UI design must include Visual contract or declare Visual design: INCOMPLETE")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args(argv)
    errors = validate(Path(args.path))
    if errors:
        print("FAIL")
        for err in errors:
            print(err)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
