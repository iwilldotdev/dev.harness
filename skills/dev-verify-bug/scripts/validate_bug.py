#!/usr/bin/env python3
"""Validate a .dev/bugs/<slug> directory. No network."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PLACEHOLDERS = ("TODO", "TBD")
PATHLINE = re.compile(r"[\w./-]+\.[A-Za-z0-9]+:\d+")
VERDICT_LINE = re.compile(r"(?:(?i:verdict)\s*:?\s*)?(PASS|FAIL|INCOMPLETE)(?=\s*(?:$|[—–:.,;(-]))")
OPEN_COMPLETENESS = re.compile(
    r"^\|[^|\n]+\|\s*[`*_]*\s*(gap|not-checked)\s*[`*_]*\s*\|",
    re.I | re.M,
)


def verdict_of(text: str) -> str | None:
    """First line whose Markdown-stripped text is the verdict, e.g. `**Verdict:** PASS`."""
    for line in text.splitlines():
        plain = re.sub(r"^[\s#>-]+", "", re.sub(r"[*_`]", "", line))
        match = VERDICT_LINE.match(plain)
        if match:
            return match.group(1)
    return None


def validate(root: Path, require_pass: bool = False) -> list[str]:
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
        verdict = verdict_of(vt)
        if verdict is None:
            errors.append("missing verdict line PASS|FAIL|INCOMPLETE")
        elif not re.search(r"^## Completeness\b", vt, re.M):
            errors.append("verdict requires Completeness")
        if require_pass and verdict != "PASS":
            errors.append("requires verdict PASS")
        if verdict == "PASS":
            if "RED" not in vt:
                errors.append("PASS requires RED pre-fix evidence")
            if "GREEN" not in vt:
                errors.append("PASS requires GREEN post-fix evidence")
            if not PATHLINE.search(vt):
                errors.append("PASS requires path:line")
            if not re.search(r"(\.{3}|merge-base|diff)", vt, re.I):
                errors.append("PASS requires diff range")
            if not re.search(r"\b(done|gap|not-checked)\b", vt):
                errors.append("Completeness requires done, gap, or not-checked")
            if OPEN_COMPLETENESS.search(vt):
                errors.append("PASS cannot contain gap or not-checked Completeness rows")
        for token in PLACEHOLDERS:
            if token in vt:
                errors.append(f"placeholder {token}")
    else:
        errors.append("missing validation.md")
        if require_pass:
            errors.append("requires verdict PASS")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument(
        "--require-pass",
        action="store_true",
        help="Fail unless validation.md verdict is PASS. Ship and agents use this.",
    )
    args = parser.parse_args(argv)
    errors = validate(Path(args.path), require_pass=args.require_pass)
    if errors:
        print("FAIL")
        for err in errors:
            print(err)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
