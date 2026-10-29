#!/usr/bin/env python3
"""Figma pack manifest for a feature or bug flow. No network.

The agent saves each `figma_get_design_context` payload as
`<flow_dir>/figma/<node-id>.json` (dash form: `3544-5710.json`) and its
verified PNG as `<node-id>.png`. This script builds `figma/pack.json`
schemaVersion 1. `--check` fails while a cited screen is missing, legacy,
truncated, or paired with a PNG that does not match the node.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CONTRACT_PATH = Path(__file__).with_name("visual_contract.py")


def load_contract():
    spec = importlib.util.spec_from_file_location("visual_contract", CONTRACT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(CONTRACT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRACT = load_contract()


def slug(node_id: str) -> str:
    return node_id.replace(":", "-")


def find_png(figma_dir: Path, node_id: str) -> Path | None:
    stem = slug(node_id)
    exact = figma_dir / f"{stem}.png"
    if exact.is_file():
        return exact
    matches = sorted(figma_dir.glob(f"{stem}-*.png"))
    return matches[0] if matches else None


def pack_entry(json_path: Path, png: Path | None) -> tuple[dict, list[str]]:
    payload, err = CONTRACT.load_json(json_path)
    if payload is None:
        return {}, [f"{json_path.name}: {err}"]
    nodes = payload.get("nodes") or []
    node = nodes[0] if isinstance(nodes, list) and nodes else {}
    node_id = node.get("id") if isinstance(node, dict) else None
    entry = {
        "json": json_path.name,
        "png": png.name if png else None,
        "nodeId": node_id,
        "fileKey": payload.get("fileKey"),
        "lastModified": payload.get("lastModified"),
        "version": payload.get("version"),
        "schemaVersion": payload.get("schemaVersion"),
        "completeness": (payload.get("completeness") or {}).get("status"),
        "truncated": payload.get("truncated"),
        "fetchedAt": datetime.fromtimestamp(json_path.stat().st_mtime, tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
    }
    errors: list[str] = []
    expected_id = json_path.stem.replace("-", ":")
    if isinstance(node_id, str) and node_id != expected_id:
        errors.append(f"{expected_id}: payload node id is {node_id}")
    if png and isinstance(node_id, str):
        data = png.read_bytes()
        entry["pngSha256"] = CONTRACT.sha256_bytes(data)
        errors.extend(CONTRACT.audit_screen(node_id, payload, data, json_path.stem))
    elif isinstance(node_id, str):
        errors.append(f"{node_id}: missing pack PNG")
    return entry, errors


def build(flow_dir: Path) -> tuple[list[str], list[str], list[str]]:
    figma_dir = flow_dir / "figma"
    figma_dir.mkdir(parents=True, exist_ok=True)
    screens: dict[str, dict] = {}
    screen_errors: list[str] = []
    for json_path in sorted(figma_dir.glob("*.json")):
        if json_path.name == "pack.json":
            continue
        payload, _ = CONTRACT.load_json(json_path)
        nodes = (payload or {}).get("nodes") or []
        node = nodes[0] if isinstance(nodes, list) and nodes else {}
        node_id = node.get("id") if isinstance(node, dict) and isinstance(node.get("id"), str) else json_path.stem.replace("-", ":")
        png = find_png(figma_dir, str(node_id))
        entry, errors = pack_entry(json_path, png)
        if not entry:
            screen_errors.extend(errors)
            continue
        screens[CONTRACT.node_key(entry.get("fileKey"), str(entry.get("nodeId") or node_id))] = entry
        screen_errors.extend(errors)

    cited = CONTRACT.cited_from_flow(flow_dir)
    missing_json: list[str] = []
    missing_png: list[str] = []
    for node_id in cited:
        stem = slug(node_id)
        if not (figma_dir / f"{stem}.json").is_file():
            missing_json.append(node_id)
        elif not find_png(figma_dir, node_id):
            missing_png.append(node_id)
    status = "complete" if not (missing_json or missing_png or screen_errors) else "incomplete"
    manifest = {
        "schemaVersion": CONTRACT.SCHEMA_VERSION,
        "status": status,
        "reasons": missing_json + missing_png + screen_errors,
        "screens": screens,
    }
    (figma_dir / "pack.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return cited, missing_json, missing_png


def check(flow_dir: Path) -> list[str]:
    cited, missing_json, missing_png = build(flow_dir)
    errors = [f"missing pack JSON for {node_id}" for node_id in missing_json]
    errors.extend(f"missing pack PNG for {node_id}" for node_id in missing_png)
    manifest, err = CONTRACT.load_json(flow_dir / "figma" / "pack.json")
    if manifest is None:
        return errors + [f"pack.json: {err}"]
    if manifest.get("schemaVersion") != CONTRACT.SCHEMA_VERSION:
        errors.append("legacy pack schema; repopulate the screens")
    errors.extend(str(reason) for reason in manifest.get("reasons") or [])
    if cited and manifest.get("status") != "complete":
        errors.append("pack status is incomplete")
    return list(dict.fromkeys(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("flow_dir", help=".dev/features/<slug> or .dev/bugs/<slug>")
    parser.add_argument("--check", action="store_true", help="Fail unless every cited screen is complete.")
    args = parser.parse_args(argv)
    flow_dir = Path(args.flow_dir)
    if args.check:
        errors = check(flow_dir)
        if errors:
            print("FAIL")
            for error in errors:
                print(error)
            return 1
        print("OK")
        return 0
    cited, missing_json, missing_png = build(flow_dir)
    if cited:
        print(f"screens cited: {len(cited)}")
    if missing_json:
        print("missing pack JSON for: " + ", ".join(missing_json))
    if missing_png:
        print("missing pack PNG for: " + ", ".join(missing_png))
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
