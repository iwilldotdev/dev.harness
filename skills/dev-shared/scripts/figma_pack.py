#!/usr/bin/env python3
"""Figma pack manifest for a feature flow. No network.

The agent saves each `figma_get_design_context` payload as
`<flow_dir>/figma/<node-id>.json` (dash form: `3544-5710.json`) and its
screenshot as `<node-id>.png`. This script builds/refreshes
`<flow_dir>/figma/pack.json` from those files and, when `design.md` exists,
checks every screen node-id cited in its `## Visual contract` has both files.

With `--check` it fails (exit 1) when a cited screen is missing from the pack.
Downstream skills (execute, verify, reviews) read the pack from disk instead of
refetching nodes; refetch happens only when `figma_get_file_meta` reports a
`lastModified` newer than the pack entry.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

NODE_ID = re.compile(r"\b(\d{1,6})[:-](\d{3,6})\b")
VISUAL = re.compile(r"^## Visual contract\b[^\n]*\n(.*?)(?=^## |\Z)", re.M | re.S)


def slug(node_id: str) -> str:
    return node_id.replace(":", "-")


def cited_node_ids(flow_dir: Path) -> list[str]:
    design = flow_dir / "design.md"
    if not design.is_file():
        return []
    visual = VISUAL.search(design.read_text(encoding="utf-8"))
    if not visual:
        return []
    ids: list[str] = []
    seen: set[str] = set()
    for match in NODE_ID.finditer(visual.group(1)):
        node_id = f"{match.group(1)}:{match.group(2)}"
        if node_id not in seen:
            seen.add(node_id)
            ids.append(node_id)
    return ids


def pack_entry(json_path: Path) -> dict | None:
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    nodes = payload.get("nodes") or []
    node = nodes[0] if isinstance(nodes, list) and nodes else {}
    return {
        "json": json_path.name,
        "png": None,
        "nodeId": node.get("id"),
        "fileKey": payload.get("fileKey"),
        "lastModified": payload.get("lastModified"),
        "fetchedAt": datetime.fromtimestamp(json_path.stat().st_mtime, tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
    }


def find_png(figma_dir: Path, node_id: str) -> Path | None:
    """`<id>.png` or `<id>-<slug>.png` (the historical naming)."""
    stem = node_id.replace(":", "-")
    exact = figma_dir / f"{stem}.png"
    if exact.is_file():
        return exact
    for path in sorted(figma_dir.glob(f"{stem}-*.png")):
        return path
    return None


def build(flow_dir: Path) -> tuple[list[str], list[str], list[str]]:
    figma_dir = flow_dir / "figma"
    figma_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict] = {}

    for json_path in sorted(figma_dir.glob("*.json")):
        if json_path.name == "pack.json":
            continue
        entry = pack_entry(json_path)
        if entry is None:
            continue
        key = f"{entry.get('fileKey') or '?'}/{entry.get('nodeId') or json_path.stem}"
        png = find_png(figma_dir, json_path.stem)
        if png:
            entry["png"] = png.name
        manifest[key] = entry

    (figma_dir / "pack.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    cited = cited_node_ids(flow_dir)
    missing_json: list[str] = []
    missing_png: list[str] = []
    for node_id in cited:
        stem = slug(node_id)
        if not (figma_dir / f"{stem}.json").is_file():
            missing_json.append(node_id)
        elif not find_png(figma_dir, node_id):
            missing_png.append(node_id)
    return cited, missing_json, missing_png


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("flow_dir", help=".dev/features/<slug>")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when a design.md screen node-id has no pack JSON or PNG.",
    )
    args = parser.parse_args(argv)
    flow_dir = Path(args.flow_dir)
    cited, missing_json, missing_png = build(flow_dir)
    if cited:
        print(f"screens cited in design.md: {len(cited)}")
    if missing_json:
        print("missing pack JSON for: " + ", ".join(missing_json))
    if missing_png:
        print("missing pack PNG for: " + ", ".join(missing_png))
    if args.check and (missing_json or missing_png):
        print("FAIL")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
