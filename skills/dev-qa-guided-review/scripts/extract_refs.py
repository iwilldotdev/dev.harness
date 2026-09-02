#!/usr/bin/env python3
"""Thin wrapper: canonical parser lives in skills/dev-shared/scripts."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

CANONICAL = (
    Path(__file__).resolve().parents[2] / "dev-shared" / "scripts" / "extract_refs.py"
)


def main() -> int:
    if not CANONICAL.is_file():
        print(f"missing canonical parser: {CANONICAL}", file=sys.stderr)
        return 1
    sys.argv[0] = str(CANONICAL)
    runpy.run_path(str(CANONICAL), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
