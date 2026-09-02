#!/usr/bin/env python3
"""Validate feature validation.md. No network."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQ = re.compile(r"REQ-\d+")
PATHLINE = re.compile(r"[\w./-]+\.[A-Za-z0-9]+:\d+")
VERDICT = re.compile(r"\b(PASS|FAIL|INCOMPLETE)\b")
DIFF = re.compile(r"(\.{3}|merge-base|diff range|[a-f0-9]{7,}\.\.\.?[a-f0-9]{7,})", re.I)
PLACEHOLDERS = ("TODO", "TBD", "looks ok", "lgtm")


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing {path}"]
    text = path.read_text(encoding="utf-8")
    if not VERDICT.search(text):
        errors.append("missing verdict PASS|FAIL|INCOMPLETE")
    if "PASS" in text:
        if not PATHLINE.search(text):
            errors.append("PASS requires path:line evidence")
        if not REQ.search(text):
            errors.append("PASS requires REQ mapping")
        if not DIFF.search(text):
            errors.append("PASS requires diff range")
        if not re.search(r"\b(outcome|test)\b", text, re.I):
            errors.append("PASS requires outcome and test mapping")
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
