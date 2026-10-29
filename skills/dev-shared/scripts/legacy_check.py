#!/usr/bin/env python3
"""Legacy (Windows-only) repo sanity checks. No network.

Runs over the files a task touched (explicit list, `--staged`, or a diff range)
and catches what a Linux run cannot: line-ending/BOM drift, `.csproj` entries
duplicated by a merge, and duplicated `appSettings` keys in `Web.config`.

Exit 1 blocks the commit/task receipt.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

CODE_EXTS = {".cs", ".cshtml", ".csproj", ".config", ".aspx", ".ashx", ".sln", ".sql"}


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def touched_files(repo: Path, args: argparse.Namespace) -> list[str]:
    if args.files:
        return [f for f in args.files.split(",") if f.strip()]
    if args.staged:
        result = git(repo, "diff", "--cached", "--name-only")
    else:
        result = git(repo, "diff", "--name-only", args.since)
    if result.returncode != 0:
        raise SystemExit(f"git failed: {result.stderr.strip()}")
    return [line for line in result.stdout.splitlines() if line.strip()]


def line_ending_drift(repo: Path, path: str) -> str | None:
    """A file that was CRLF at HEAD must stay CRLF (and vice versa)."""
    head = git(repo, "show", f"HEAD:{path}")
    work = (repo / path).read_bytes()
    if head.returncode != 0:
        return None  # new file: nothing to drift from
    base = head.stdout.encode("utf-8", "surrogateescape")
    base_crlf = base.count(b"\r\n")
    base_lf = base.count(b"\n") - base_crlf
    work_crlf = work.count(b"\r\n")
    work_lf = work.count(b"\n") - work_crlf
    if base_crlf > 0 and work_lf > 0:
        return f"{path}: CRLF file gained {work_lf} bare-LF lines"
    if base_lf > 0 and work_crlf > 0:
        return f"{path}: LF file gained {work_crlf} CRLF lines"
    return None


def bom_drift(repo: Path, path: str) -> str | None:
    head = git(repo, "show", f"HEAD:{path}")
    if head.returncode != 0:
        return None
    base = head.stdout.encode("utf-8", "surrogateescape")
    work = (repo / path).read_bytes()
    base_bom = base.startswith(b"\xef\xbb\xbf")
    work_bom = work.startswith(b"\xef\xbb\xbf")
    if base_bom != work_bom:
        state = "lost" if base_bom else "gained"
        return f"{path}: BOM {state} (legacy builds expect it unchanged)"
    return None


def duplicate_compile(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return [f"{path}: not valid XML"]
    seen: dict[str, int] = {}
    for node in root.iter("Compile"):
        include = node.get("Include", "").strip()
        if not include:
            continue
        key = include.replace("\\", "/").lower()
        seen[key] = seen.get(key, 0) + 1
    for include, count in seen.items():
        if count > 1:
            errors.append(f"{path}: {count} <Compile Include=\"{include}\">")
    return errors


def duplicate_appsettings(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return [f"{path}: not valid XML"]
    seen: dict[str, int] = {}
    for setting in root.iter("add"):
        key = setting.get("key") or setting.get("name")
        if not key:
            continue
        seen[key] = seen.get(key, 0) + 1
    for key, count in seen.items():
        if count > 1:
            errors.append(f"{path}: {count} appSettings keys {key!r}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo")
    parser.add_argument("--files", help="Comma-separated paths (relative to the repo)")
    parser.add_argument("--staged", action="store_true", help="Check the staged diff")
    parser.add_argument("--since", default="HEAD", help="Diff range base (default HEAD)")
    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()
    errors: list[str] = []

    for path in touched_files(repo, args):
        if not path.lower().endswith(tuple(CODE_EXTS)):
            continue
        target = repo / path
        if not target.is_file():
            continue
        for check in (line_ending_drift, bom_drift):
            error = check(repo, path)
            if error:
                errors.append(error)
        if path.lower().endswith(".csproj"):
            errors.extend(duplicate_compile(target))
        if path.lower().endswith(".config"):
            errors.extend(duplicate_appsettings(target))

    if errors:
        print("FAIL")
        for error in errors:
            print(error)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
