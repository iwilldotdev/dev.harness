#!/usr/bin/env python3
"""Validate feature spec.md. No network."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQ = re.compile(r"REQ-\d+")
WHEN = re.compile(r"(when |if |the system shall|ears|quando |então|then )", re.I)
PLACEHOLDERS = ("TODO", "TBD", "lorem ipsum", "xxx")
ORIGIN = re.compile(r"(jira|gate|figma|intake|field|description|ac\b)", re.I)
SCOPE = re.compile(r"(out of scope|fora de escopo|scope)", re.I)
RISK = re.compile(r"(risk|risco)", re.I)
OUTCOME = re.compile(r"(outcome|expected|então|then the)", re.I)
UI_REF = re.compile(r"(figma|node-id)", re.I)
VISUAL = re.compile(r"^## Visual contract\b[^\n]*\n(.*?)(?=^## |\Z)", re.M | re.S)
NODE_ID = re.compile(r"\b\d+[:-]\d+\b")


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing {path}"]
    text = path.read_text(encoding="utf-8")
    ids = REQ.findall(text)
    if not ids:
        errors.append("no REQ-NNN identifiers")
    if len(ids) != len(set(ids)):
        errors.append("duplicate REQ ids")
    if not WHEN.search(text):
        errors.append("requirements must be testable (EARS or when/then)")
    if not ORIGIN.search(text):
        errors.append("each spec must cite origin evidence (Jira/gate/intake/Figma)")
    if not SCOPE.search(text):
        errors.append("spec must declare out of scope")
    if not RISK.search(text):
        errors.append("spec must declare risk")
    if not OUTCOME.search(text):
        errors.append("spec must declare expected outcomes")
    if UI_REF.search(text):
        visual = VISUAL.search(text)
        if not visual:
            errors.append("UI spec that cites Figma must include Visual contract")
        elif not NODE_ID.search(visual.group(1)):
            errors.append("Visual contract must cite the screen node-id")
    for token in PLACEHOLDERS:
        if token.lower() in text.lower():
            errors.append(f"placeholder {token}")
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
