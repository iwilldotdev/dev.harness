#!/usr/bin/env python3
"""Validate feature tasks.md. No network."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQ = re.compile(r"REQ-\d+")
PLACEHOLDERS = ("TODO", "TBD", "implement later", "similar to task")
FILE = re.compile(r"(\.[A-Za-z0-9]{1,8}\b|/[\w.-]+|files?:)", re.I)
IFACE = re.compile(r"(consumes|produces|interface)", re.I)


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing {path}"]
    text = path.read_text(encoding="utf-8")
    if not REQ.search(text):
        errors.append("no REQ-NNN coverage")
    if "gate" not in text.lower():
        errors.append("every task needs an observable Gate")
    if not re.search(r"(red|failing test)", text, re.I):
        errors.append("tasks must include RED/failing test")
    if not re.search(r"(green|passing test)", text, re.I):
        errors.append("tasks must include GREEN/passing test")
    if not FILE.search(text):
        errors.append("tasks must list exact files")
    if not IFACE.search(text):
        errors.append("tasks must list interfaces consumed/produced")
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
