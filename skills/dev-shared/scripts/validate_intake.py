#!/usr/bin/env python3
"""Validate a feature or bug visual manifest. No network."""

from __future__ import annotations

import argparse
import importlib.util
import sys
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


def validate(flow_dir: Path) -> list[str]:
    path = flow_dir / "visual-manifest.json"
    if not path.is_file():
        cited = CONTRACT.cited_from_flow(flow_dir)
        if cited:
            return ["visual-manifest.json is required when a screen is cited"]
        return []
    manifest, err = CONTRACT.load_json(path)
    if manifest is None:
        return [f"visual-manifest.json: {err}"]
    errors = CONTRACT.manifest_errors(manifest)
    cited = set(CONTRACT.cited_from_flow(flow_dir))
    covered = {
        str(entry.get("nodeId"))
        for entry in manifest.get("entries") or []
        if isinstance(entry, dict)
    }
    missing = sorted(cited - covered)
    if missing:
        errors.append("manifest does not cover screens: " + ", ".join(missing))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("flow_dir")
    args = parser.parse_args(argv)
    errors = validate(Path(args.flow_dir))
    if errors:
        print("FAIL")
        for error in errors:
            print(error)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
