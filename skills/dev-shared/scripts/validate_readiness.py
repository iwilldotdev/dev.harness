#!/usr/bin/env python3
"""Validate <flow-dir>/reviews/readiness.md against the working tree. No network."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

REVIEWS = ("MR", "QA")
LINE = re.compile(r"^(MR|QA) (verdict|open rows|reviewed):\s*(\S+)\s*$")


def parse(text: str) -> dict[tuple[str, str], str]:
    fields: dict[tuple[str, str], str] = {}
    for line in text.splitlines():
        plain = re.sub(r"^[\s>-]+", "", re.sub(r"[*`]", "", line))
        match = LINE.match(plain)
        if match:
            fields[(match.group(1), match.group(2))] = match.group(3)
    return fields


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def validate(flow_dir: Path, repo: Path) -> list[str]:
    receipt = flow_dir / "reviews" / "readiness.md"
    if not receipt.is_file():
        return [f"missing {receipt}"]
    fields = parse(receipt.read_text(encoding="utf-8"))
    errors: list[str] = []
    for review in REVIEWS:
        verdict = fields.get((review, "verdict"))
        open_rows = fields.get((review, "open rows"))
        sha = fields.get((review, "reviewed"))
        if verdict is None or open_rows is None or sha is None:
            errors.append(f"{review}: needs verdict, open rows, and reviewed")
            continue
        if verdict != "APPROVE":
            errors.append(f"{review}: verdict {verdict} is not APPROVE")
        if open_rows != "0":
            errors.append(f"{review}: {open_rows} open Completeness rows")
        if git(repo, "rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}").returncode != 0:
            errors.append(f"{review}: reviewed commit {sha} not found")
            continue
        diff = git(repo, "diff", "--quiet", sha, "--", ".", ":(exclude).dev")
        if diff.returncode == 1:
            errors.append(f"{review}: files outside .dev changed since the review at {sha}")
        elif diff.returncode != 0:
            errors.append(f"{review}: git diff failed: {diff.stderr.strip()}")
    listed = git(repo, "ls-files", "--others", "--exclude-standard")
    if listed.returncode != 0:
        errors.append(f"git ls-files failed: {listed.stderr.strip()}")
    else:
        untracked = [
            path
            for path in listed.stdout.splitlines()
            if path and path != ".dev" and not path.startswith(".dev/")
        ]
        if untracked:
            errors.append("untracked files outside .dev: " + ", ".join(untracked))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("flow_dir", help=".dev/features/<slug> or .dev/bugs/<slug>")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args(argv)
    errors = validate(Path(args.flow_dir), Path(args.repo))
    if errors:
        print("FAIL")
        for err in errors:
            print(err)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
