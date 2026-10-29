#!/usr/bin/env python3
"""Cross Jira tickets with Figma frames. No network.

Inputs (either works):
- `--frames frames.json` — the payload of `figma_get_frames` ({"frames": [...]});
- `--keys PROD-3289,PROD-3288` or `--tickets tickets.json` — a Jira list
  (`{"issues":[{"key":...}]}`) or a plain array of keys; when omitted, keys are
  extracted from the frame names themselves.

The join is the frame name containing the ticket key (case-insensitive). The
output is a draft `ticket x frame x repo` mapping table for intake.md; rows
without a counterpart are listed separately for the gap round.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

JIRA_KEY_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b")
JIRA_FALSE_POSITIVES = frozenset({"UTF-8", "ISO-8601", "SHA-1", "SHA-256", "SHA-512", "MD5-1"})


def load_frames(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    frames = payload.get("frames", payload) if isinstance(payload, dict) else payload
    return [frame for frame in frames if isinstance(frame, dict) and frame.get("id")]


def load_keys(args: argparse.Namespace, frames: list[dict]) -> list[str]:
    keys: list[str] = []
    if args.keys:
        keys = [key.strip().upper() for key in args.keys.split(",") if key.strip()]
    elif args.tickets:
        payload = json.loads(Path(args.tickets).read_text(encoding="utf-8"))
        issues = payload.get("issues", payload) if isinstance(payload, dict) else payload
        for issue in issues:
            key = issue.get("key") if isinstance(issue, dict) else issue
            if isinstance(key, str):
                keys.append(key.upper())
    else:
        names = " ".join(str(frame.get("name", "")) for frame in frames)
        keys = [key for key in JIRA_KEY_RE.findall(names) if key not in JIRA_FALSE_POSITIVES]
    seen: set[str] = set()
    return [key for key in keys if not (key in seen or seen.add(key))]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--frames", help="figma_get_frames payload JSON")
    parser.add_argument("--keys", help="Comma-separated Jira keys")
    parser.add_argument("--tickets", help="Jira search payload JSON ({issues:[{key}]})")
    args = parser.parse_args(argv)
    if not args.frames:
        parser.error("--frames is required")
    frames = load_frames(Path(args.frames))
    keys = load_keys(args, frames)

    by_key: dict[str, list[dict]] = {key: [] for key in keys}
    unmatched_frames: list[dict] = []
    for frame in frames:
        name = str(frame.get("name", ""))
        hit = False
        for key in keys:
            if key.lower() in name.lower():
                by_key[key].append(frame)
                hit = True
        if not hit and not JIRA_KEY_RE.search(name):
            unmatched_frames.append(frame)

    print("| Ticket | Frame node-id | Frame name | Page |")
    print("| --- | --- | --- | --- |")
    open_tickets: list[str] = []
    for key in keys:
        if not by_key[key]:
            open_tickets.append(key)
            print(f"| {key} | MISSING | | |")
            continue
        for frame in by_key[key]:
            print(
                f"| {key} | {frame.get('id')} | {frame.get('name')} | {frame.get('page', '')} |"
            )
    if unmatched_frames:
        print()
        print("Frames sem ticket no nome (confirmar no gate):")
        for frame in unmatched_frames:
            print(f"- {frame.get('id')} {frame.get('name')} ({frame.get('page', '')})")
    if open_tickets:
        print()
        print("Tickets sem frame (gap round): " + ", ".join(open_tickets))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
