#!/usr/bin/env python3
"""Conventional Commits; reject attribution trailers. No network."""

from __future__ import annotations

import argparse
import re
import sys

HEADER = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([a-z0-9._/-]+\))?(!)?: .+"
)
FORBIDDEN = (
    "Co-authored-by:",
    "Made-with:",
    "Made-With:",
)


def check(message: str) -> list[str]:
    errors: list[str] = []
    first = message.strip().splitlines()[0] if message.strip() else ""
    if not first or not HEADER.match(first):
        errors.append("header must be Conventional Commits (type: subject)")
    for token in FORBIDDEN:
        if token.lower() in message.lower():
            errors.append(f"forbidden trailer {token}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check commit message")
    parser.add_argument("--message", required=True)
    args = parser.parse_args(argv)
    errors = check(args.message)
    if errors:
        print("FAIL")
        for err in errors:
            print(err)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
