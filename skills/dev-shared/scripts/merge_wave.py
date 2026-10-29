#!/usr/bin/env python3
"""Merge task worktrees into the feature branch, wave by wave. No network.

Replaces the orchestrator's hand merges (the DEV-9436 epic hit a controller
collision, an add/add, and a duplicated `<Compile>` merged silently).

For each worktree (in the order given):
1. reads the worktree's current branch,
2. `git merge --no-ff --no-edit <task-branch>` on the target branch,
3. on conflict: `git merge --abort` and stop with the conflicting files,
4. after each successful merge: refuses conflict markers, duplicated
   `<Compile>` entries, and duplicated `appSettings` keys (legacy_check rules).

The repo checkout must be clean and on the target branch before calling.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MARKER = re.compile(r"^(<<<<<<<|>>>>>>>|=======)", re.M)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def changed_files(repo: Path) -> list[str]:
    result = git(repo, "diff", "--name-only", "HEAD@{1}", "HEAD")
    return [line for line in result.stdout.splitlines() if line.strip()]


def duplicate_compile(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return [f"{path}: not valid XML after merge"]
    seen: dict[str, int] = {}
    for node in root.iter("Compile"):
        include = node.get("Include", "").strip()
        if include:
            seen[include.replace("\\", "/").lower()] = seen.get(
                include.replace("\\", "/").lower(), 0
            ) + 1
    for include, count in seen.items():
        if count > 1:
            errors.append(f"{path}: {count} <Compile Include=\"{include}\"> after merge")
    return errors


def duplicate_appsettings(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return [f"{path}: not valid XML after merge"]
    seen: dict[str, int] = {}
    for setting in root.iter("add"):
        key = setting.get("key") or setting.get("name")
        if key:
            seen[key] = seen.get(key, 0) + 1
    for key, count in seen.items():
        if count > 1:
            errors.append(f"{path}: {count} appSettings keys {key!r} after merge")
    return errors


def post_merge_checks(repo: Path) -> list[str]:
    errors: list[str] = []
    for path in changed_files(repo):
        target = repo / path
        if not target.is_file():
            continue
        text = target.read_text(encoding="utf-8", errors="replace")
        if MARKER.search(text):
            errors.append(f"{path}: conflict marker committed")
        if path.lower().endswith(".csproj"):
            errors.extend(duplicate_compile(target))
        if path.lower().endswith(".config"):
            errors.extend(duplicate_appsettings(target))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", help="Checkout on the target feature branch")
    parser.add_argument("worktrees", nargs="+", help="Task worktree paths, in merge order")
    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()

    status = git(repo, "status", "--porcelain")
    if status.returncode != 0 or status.stdout.strip():
        print(f"FAIL: {repo} is not clean; commit or park unrelated changes first")
        return 1

    for worktree in args.worktrees:
        wt = Path(worktree).resolve()
        branch = git(wt, "branch", "--show-current").stdout.strip()
        if not branch:
            print(f"FAIL: {wt} has no current branch")
            return 1
        exists = git(repo, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}")
        if exists.returncode != 0:
            print(
                f"FAIL: {branch} is not a local branch of {repo}; "
                "fetch it or run from the repo that owns the worktrees"
            )
            return 1
        merge = git(repo, "merge", "--no-ff", "--no-edit", branch)
        if merge.returncode != 0:
            conflicts = [
                line.split(":", 1)[-1].strip()
                for line in (merge.stdout + merge.stderr).splitlines()
                if "CONFLICT" in line
            ]
            merge_state = git(repo, "rev-parse", "--verify", "--quiet", "MERGE_HEAD")
            if merge_state.returncode == 0:
                git(repo, "merge", "--abort")
            if conflicts:
                print(f"FAIL: merge {branch} conflicted; aborted. Files:")
                for conflict in conflicts:
                    print(f"  {conflict}")
                print("Resolve in the task worktree (or union regions by hand) and rerun.")
            else:
                print(f"FAIL: merge {branch} failed before merging:\n{merge.stderr.strip()}")
            return 1
        errors = post_merge_checks(repo)
        if errors:
            print(f"FAIL: post-merge checks failed for {branch}:")
            for error in errors:
                print(f"  {error}")
            return 1
        print(f"merged {branch} ({merge.stdout.splitlines()[0] if merge.stdout else 'ok'})")
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
