#!/usr/bin/env python3
"""Validate a .dev/bugs/<slug> directory. No network."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PLACEHOLDERS = ("TODO", "TBD")
PATHLINE = re.compile(r"[\w./-]+\.[A-Za-z0-9]+:\d+")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"missing dir {root}"]
    intake = root / "intake.md"
    repro = root / "reproduction.md"
    hypo = root / "hypothesis.md"
    validation = root / "validation.md"
    if intake.is_file():
        text = intake.read_text(encoding="utf-8")
        if "expected" not in text.lower() or "actual" not in text.lower():
            errors.append("intake needs expected and actual")
    else:
        errors.append("missing intake.md")
    if not repro.is_file():
        errors.append("missing reproduction.md")
    if hypo.is_file():
        ht = hypo.read_text(encoding="utf-8")
        if "hypothesis" not in ht.lower():
            errors.append("hypothesis.md must state a hypothesis")
        if not re.search(r"falsification:", ht, re.I):
            errors.append("hypothesis must be falsifiable")
        if "cause" not in ht.lower() and "root" not in ht.lower():
            errors.append("hypothesis must name a cause")
    if validation.is_file():
        vt = validation.read_text(encoding="utf-8")
        if re.search(r"\bPASS\b", vt):
            if "RED" not in vt:
                errors.append("PASS requires RED pre-fix evidence")
            if "GREEN" not in vt:
                errors.append("PASS requires GREEN post-fix evidence")
            if not PATHLINE.search(vt):
                errors.append("PASS requires path:line")
            if not re.search(r"(\.{3}|merge-base|diff)", vt, re.I):
                errors.append("PASS requires diff range")
        for token in PLACEHOLDERS:
            if token in vt:
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
