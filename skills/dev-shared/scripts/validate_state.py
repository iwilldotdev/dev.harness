#!/usr/bin/env python3
"""Validate .dev/STATE.md. No network."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED = ("flow:", "gate:", "branch:", "next:", "artifact:", "merge-base:")
FLOW_OK = {"feature", "bug", "none"}
MODE_OK = {"manual", "agent"}
PLACEHOLDERS = ("TODO", "TBD", "lorem", "xxx")


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing {path}"]
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    for key in REQUIRED:
        if key not in lower:
            errors.append(f"missing field {key.rstrip(':')}")
    flow = None
    for line in text.splitlines():
        if line.lower().startswith("flow:"):
            flow = line.split(":", 1)[1].strip().lower()
    if flow and flow not in FLOW_OK:
        errors.append(f"invalid flow {flow!r}")
    mode = None
    for line in text.splitlines():
        if line.lower().startswith("mode:"):
            mode = line.split(":", 1)[1].strip().lower()
    if mode is not None and mode not in MODE_OK:
        errors.append(f"invalid mode {mode!r}")
    for token in PLACEHOLDERS:
        if re.search(rf"\b{token}\b", text, re.I):
            errors.append(f"placeholder {token}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate .dev/STATE.md")
    parser.add_argument("path", nargs="?", default=".dev/STATE.md")
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
