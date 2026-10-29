#!/usr/bin/env python3
"""Shared Figma visual-contract checks. No network."""

from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path

SCHEMA_VERSION = 1
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
NODE_ID = re.compile(r"\b(\d{1,6})[:-](\d{3,6})\b")
VISUAL = re.compile(r"^## Visual contract\b[^\n]*\n(.*?)(?=^## |\Z)", re.M | re.S)
ENTRY_FIELDS = ("id", "jiraKey", "requirement", "fileKey", "nodeId", "state", "viewport", "figmaRevision", "evidence")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def png_size(data: bytes) -> tuple[int, int] | str:
    if not data.startswith(PNG_SIGNATURE) or len(data) < 24 or data[12:16] != b"IHDR":
        return "png is not decodable"
    width, height = struct.unpack(">II", data[16:24])
    if width <= 0 or height <= 0:
        return "png has no visible dimensions"
    return width, height


def node_key(file_key: str | None, node_id: str) -> str:
    return f"{file_key or '?'}/{node_id}"


def cited_ids(text: str) -> list[str]:
    visual = VISUAL.search(text)
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


def _remember(ids: list[str], seen: set[str], node_id: str) -> None:
    if node_id not in seen:
        seen.add(node_id)
        ids.append(node_id)


def cited_from_flow(flow_dir: Path) -> list[str]:
    """Union of every visual contract in the flow, including prior cycles and packed screens.

    Renaming design.md or writing an empty later contract does not drop a screen.
    """
    ids: list[str] = []
    seen: set[str] = set()
    if not flow_dir.is_dir():
        return ids
    for path in sorted(flow_dir.rglob("*.md")):
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf-8")
        section = VISUAL.search(source)
        blob = section.group(1) if section else ""
        if path.name.startswith("intake"):
            blob += "\n" + "\n".join(
                line for line in source.splitlines() if re.search(r"\bscreen\b", line, re.I)
            )
        for match in NODE_ID.finditer(blob):
            _remember(ids, seen, f"{match.group(1)}:{match.group(2)}")
    figma = flow_dir / "figma"
    if figma.is_dir():
        for path in sorted(figma.iterdir()):
            if not path.is_file() or path.name == "pack.json":
                continue
            match = NODE_ID.search(path.stem)
            if match:
                _remember(ids, seen, f"{match.group(1)}:{match.group(2)}")
    return ids


def load_json(path: Path) -> tuple[dict | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as err:
        return None, str(err)
    if not isinstance(payload, dict):
        return None, "JSON root must be an object"
    return payload, None


def audit_screen(node_id: str, payload: dict, png: bytes, filename_stem: str) -> list[str]:
    errors: list[str] = []
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"{node_id}: legacy or missing schemaVersion")
    if payload.get("completeness", {}).get("status") != "complete":
        errors.append(f"{node_id}: design context is not complete")
    if payload.get("truncated") is not False:
        errors.append(f"{node_id}: truncated payload")
    missing = payload.get("missingNodeIds") or []
    if missing:
        errors.append(f"{node_id}: missing nodes {missing}")
    warnings = [item for item in payload.get("warnings") or [] if not str(item).startswith("variables:")]
    if warnings:
        errors.append(f"{node_id}: warnings {warnings}")
    nodes = payload.get("nodes") or []
    node = nodes[0] if isinstance(nodes, list) and nodes else {}
    if not isinstance(node, dict) or node.get("id") != node_id:
        errors.append(f"{node_id}: payload node id does not match {filename_stem}")
    size = png_size(png)
    if isinstance(size, str):
        errors.append(f"{node_id}: {size}")
    else:
        expected = node.get("size") if isinstance(node, dict) else None
        scale = 1
        screenshot = payload.get("screenshot") or {}
        if isinstance(screenshot, dict) and screenshot.get("scale") not in (None, 1):
            scale = float(screenshot["scale"])
        if isinstance(expected, dict) and "width" in expected and "height" in expected:
            width = int(round(float(expected["width"]) * scale))
            height = int(round(float(expected["height"]) * scale))
            if abs(size[0] - width) > 1 or abs(size[1] - height) > 1:
                errors.append(f"{node_id}: png {size[0]}x{size[1]} != node {width}x{height}")
    if not payload.get("lastModified"):
        errors.append(f"{node_id}: missing lastModified")
    return errors


def manifest_errors(manifest: dict) -> list[str]:
    if manifest.get("schemaVersion") != SCHEMA_VERSION:
        return ["visual-manifest schemaVersion must be 1"]
    unresolved = manifest.get("unresolved") or []
    errors = [f"unresolved reference: {item}" for item in unresolved]
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        return errors + ["visual-manifest needs at least one entry"]
    seen: set[str] = set()
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(f"entry {index} is not an object")
            continue
        for field in ENTRY_FIELDS:
            if entry.get(field) in (None, ""):
                errors.append(f"entry {index} missing {field}")
        viewport = entry.get("viewport")
        if not isinstance(viewport, dict) or not viewport.get("width") or not viewport.get("height"):
            errors.append(f"entry {index} viewport needs width and height")
        entry_id = str(entry.get("id"))
        if entry_id in seen:
            errors.append(f"duplicate manifest entry {entry_id}")
        seen.add(entry_id)
        if not entry.get("route") and not entry.get("adapter"):
            errors.append(f"entry {entry_id} needs a route or adapter")
    return errors


def evidence_errors(flow_dir: Path, reviewed_shas: set[str]) -> list[str]:
    path = flow_dir / "visual-manifest.json"
    cited = cited_from_flow(flow_dir)
    needs = path.is_file() or bool(cited)
    if not needs:
        return []
    if not path.is_file():
        return ["visual-manifest.json is required when the flow cites a screen: " + ", ".join(cited)]
    manifest, err = load_json(path)
    if manifest is None:
        return [f"visual-manifest.json: {err}"]
    errors = manifest_errors(manifest)
    if manifest.get("schemaVersion") != SCHEMA_VERSION:
        return errors
    passed = 0
    entries = manifest.get("entries") if isinstance(manifest.get("entries"), list) else []
    covered = {
        str(entry.get("nodeId"))
        for entry in entries
        if isinstance(entry, dict) and entry.get("nodeId")
    }
    missing = [node_id for node_id in cited if node_id not in covered]
    if missing:
        errors.append("manifest does not cover screens: " + ", ".join(missing))
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        evidence = flow_dir / str(entry.get("evidence") or "")
        if not evidence.is_file():
            errors.append(f"missing evidence for {entry.get('id')}")
            continue
        result, result_err = load_json(evidence)
        if result is None:
            errors.append(f"{entry.get('id')}: {result_err}")
            continue
        sha_ok = not reviewed_shas or all(result.get("gitSha") == sha for sha in reviewed_shas)
        if result.get("status") != "pass":
            errors.append(f"{entry.get('id')}: evidence status is not pass")
        if result.get("entryId") != entry.get("id"):
            errors.append(f"{entry.get('id')}: evidence entryId mismatch")
        if not sha_ok:
            errors.append(f"{entry.get('id')}: evidence gitSha does not match the reviewed commit")
        if result.get("figmaRevision") != entry.get("figmaRevision"):
            errors.append(f"{entry.get('id')}: evidence figmaRevision is stale")
        for name in ("app.png", "figma.png", "diff.png"):
            if not (evidence.parent / name).is_file():
                errors.append(f"{entry.get('id')}: missing {name}")
        if result.get("status") == "pass" and sha_ok and result.get("figmaRevision") == entry.get("figmaRevision"):
            passed += 1
    receipt = flow_dir / "reviews" / "readiness.md"
    if receipt.is_file() and entries:
        recorded = receipt_ratio(receipt.read_text(encoding="utf-8"))
        expected = f"{passed}/{len(entries)}"
        if recorded is None:
            errors.append("QA: needs a figma-screens line derived from visual evidence")
        elif recorded != expected:
            errors.append(f"QA: figma-screens {recorded} != calculated {expected}")
    return errors


def receipt_ratio(text: str) -> str | None:
    for line in text.splitlines():
        plain = re.sub(r"^[\s>-]+", "", re.sub(r"[*`]", "", line))
        match = re.match(r"^QA figma-screens:\s*(\d+/\d+)\s*$", plain)
        if match:
            return match.group(1)
    return None
