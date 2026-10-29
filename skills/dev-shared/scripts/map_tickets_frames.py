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
    parser.add_argument("--overrides", help="JSON list of {ticket, nodeId, reason}")
    parser.add_argument("--strict", action="store_true", help="Fail when a ticket or override has no frame.")
    args = parser.parse_args(argv)
    if not args.frames:
        parser.error("--frames is required")
    frames = load_frames(Path(args.frames))
    keys = load_keys(args, frames)
    overrides: dict[str, dict] = {}
    if args.overrides:
        payload = json.loads(Path(args.overrides).read_text(encoding="utf-8"))
        for item in payload:
            if isinstance(item, dict) and item.get("ticket") and item.get("nodeId") and item.get("reason"):
                overrides[str(item["ticket"]).upper()] = item

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

    by_id = {str(frame.get("id")): frame for frame in frames}
    print("| Ticket | Frame node-id | Frame name | Page path | Section path | Source |")
    print("| --- | --- | --- | --- | --- | --- |")
    open_tickets: list[str] = []
    for key in keys:
        override = overrides.get(key)
        chosen = by_key[key]
        source = "name"
        if override:
            frame = by_id.get(str(override["nodeId"]))
            chosen = [frame] if frame else []
            source = "override"
            if not frame:
                open_tickets.append(key)
        if not chosen:
            if key not in open_tickets:
                open_tickets.append(key)
            print(f"| {key} | MISSING | | | | {source} |")
            continue
        for frame in chosen:
            page_path = " / ".join(frame.get("pagePath") or [frame.get("page", "")])
            section_path = " / ".join(frame.get("sectionPath") or [])
            print(
                f"| {key} | {frame.get('id')} | {frame.get('name')} | {page_path} | {section_path} | {source} |"
            )
    if unmatched_frames:
        print()
        print("Frames sem ticket no nome (confirmar no gate):")
        for frame in unmatched_frames:
            print(f"- {frame.get('id')} {frame.get('name')} ({frame.get('page', '')})")
    if open_tickets:
        print()
        print("Tickets sem frame (gap round): " + ", ".join(open_tickets))
    if args.strict and open_tickets:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
