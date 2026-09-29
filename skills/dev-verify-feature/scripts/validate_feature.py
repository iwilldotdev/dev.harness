#!/usr/bin/env python3
"""Validate feature validation.md. No network."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQ = re.compile(r"REQ-\d+")
PATHLINE = re.compile(r"[\w./-]+\.[A-Za-z0-9]+:\d+")
DIFF = re.compile(r"(\.{3}|merge-base|diff range|[a-f0-9]{7,}\.\.\.?[a-f0-9]{7,})", re.I)
VERDICT_LINE = re.compile(r"(?:(?i:verdict)\s*:?\s*)?(PASS|FAIL|INCOMPLETE)(?=\s*(?:$|[—–:.,;(-]))")
OPEN_COMPLETENESS = re.compile(
    r"^\|[^|\n]+\|\s*[`*_]*\s*(gap|not-checked)\s*[`*_]*\s*\|",
    re.I | re.M,
)
PLACEHOLDERS = ("TODO", "TBD", "looks ok", "lgtm")


def verdict_of(text: str) -> str | None:
    """First line whose Markdown-stripped text is the verdict, e.g. `**Verdict:** PASS`."""
    for line in text.splitlines():
        plain = re.sub(r"^[\s#>-]+", "", re.sub(r"[*_`]", "", line))
        match = VERDICT_LINE.match(plain)
        if match:
            return match.group(1)
    return None


def validate(path: Path, require_pass: bool = False) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing {path}"]
    text = path.read_text(encoding="utf-8")
    verdict = verdict_of(text)
    if verdict is None:
        errors.append("missing verdict line PASS|FAIL|INCOMPLETE")
    elif not re.search(r"^## Completeness\b", text, re.M):
        errors.append("verdict requires Completeness")
    if require_pass and verdict != "PASS":
        errors.append("requires verdict PASS")
    if verdict == "PASS":
        if not PATHLINE.search(text):
            errors.append("PASS requires path:line evidence")
        if not REQ.search(text):
            errors.append("PASS requires REQ mapping")
        if not DIFF.search(text):
            errors.append("PASS requires diff range")
        if not re.search(r"\b(outcome|test)\b", text, re.I):
            errors.append("PASS requires outcome and test mapping")
        if not re.search(r"\b(done|gap|not-checked)\b", text):
            errors.append("Completeness requires done, gap, or not-checked")
        if OPEN_COMPLETENESS.search(text):
            errors.append("PASS cannot contain gap or not-checked Completeness rows")
    for token in PLACEHOLDERS:
        if token.lower() in text.lower():
            errors.append(f"placeholder {token}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument(
        "--require-pass",
        action="store_true",
        help="Fail unless the verdict line is PASS. Ship and agents use this.",
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
