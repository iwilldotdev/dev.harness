#!/usr/bin/env python3
"""Validate feature design.md visual contract. No network."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PLACEHOLDERS = ("TODO", "TBD", "add validation")
UI_REF = re.compile(r"(figma|node-id)", re.I)
INCOMPLETE = re.compile(r"visual design\s*[:=]\s*INCOMPLETE", re.I)
VISUAL = re.compile(r"^## Visual contract\b[^\n]*\n(.*?)(?=^## |\Z)", re.M | re.S)
NODE_ID = re.compile(r"\b\d+[:-]\d+\b")


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
