#!/usr/bin/env python3
"""Canonical extractors for the dev.harness (Jira, Figma, GitLab). No network."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

JIRA_KEY_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b")
FIGMA_URL_RE = re.compile(
    r"https?://(?:www\.)?figma\.com/(?:file|design|proto|board|slides|make)"
    r"/([a-zA-Z0-9]+)(?:/[^\s\"'<>]*)?",
    re.IGNORECASE,
)
GITLAB_MR_URL_RE = re.compile(
    r"https?://[^\s\"'<>]+/-/merge_requests/(\d+)",
    re.IGNORECASE,
)
GITLAB_BANG_RE = re.compile(
    r"\b([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+)!(\d+)\b"
)
GITLAB_SSH_RE = re.compile(
    r"^(?:git@|ssh://(?:[^@/]+@)?)([^/:]+)[:/](.+?)(?:\.git)?$"
)
# Query / prose (ticket, metadata dump). Does not resolve Figma internal hyperlinks.
FIGMA_NODE_ATTR_RE = re.compile(
    r"node[-_]?id\s*[=:]\s*(\d+)[-:](\d+)",
    re.IGNORECASE,
)
FIGMA_XML_ID_RE = re.compile(r'\bid="(\d+:\d+)"')
# Bare ids like 85:1999 / 203:11374; right side ≥3 digits avoids clock times (12:30).
FIGMA_BARE_NODE_RE = re.compile(r"\b(\d{1,6}):(\d{3,6})\b")

JIRA_FALSE_POSITIVES = frozenset(
    {
        "UTF-8",
        "ISO-8601",
        "SHA-1",
        "SHA-256",
        "SHA-512",
        "MD5-1",
    }
)


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def extract_jira_keys(text: str) -> list[str]:
    keys: list[str] = []
    for match in JIRA_KEY_RE.finditer(text):
        key = match.group(0)
        if key in JIRA_FALSE_POSITIVES:
            continue
        keys.append(key)
    return _unique(keys)


def _parse_figma_node_ids(raw: str | None) -> list[str]:
    if not raw:
        return []
    ids: list[str] = []
    for part in re.split(r"[,\s]+", raw):
        part = part.strip()
        if not part:
            continue
        ids.append(part.replace("-", ":"))
    return _unique(ids)


def _normalize_figma_node_id(left: str, right: str) -> str:
    return f"{left}:{right}"


def extract_figma_node_ids(text: str) -> list[str]:
    """IDs in URLs, node-id= attrs, XML id=, and bare N:MMM. Not Figma hyperlinks."""
    ids: list[str] = []
    for entry in extract_figma(text):
        ids.extend(entry.get("node_ids") or [])
    for match in FIGMA_NODE_ATTR_RE.finditer(text):
        ids.append(_normalize_figma_node_id(match.group(1), match.group(2)))
    for match in FIGMA_XML_ID_RE.finditer(text):
        ids.append(match.group(1))
    for match in FIGMA_BARE_NODE_RE.finditer(text):
        ids.append(_normalize_figma_node_id(match.group(1), match.group(2)))
    return _unique(ids)


def extract_figma(text: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[str, ...]]] = set()
    for match in FIGMA_URL_RE.finditer(text):
        url = match.group(0).rstrip(").,];")
        file_key = match.group(1)
        node_ids: list[str] = []
        try:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            raw_nodes = (qs.get("node-id") or qs.get("node_id") or [None])[0]
            node_ids = _parse_figma_node_ids(raw_nodes)
        except ValueError:
            node_ids = []
        sig = (file_key, tuple(node_ids))
        if sig in seen:
            continue
        seen.add(sig)
        entry: dict[str, Any] = {"url": url, "file_key": file_key}
        if node_ids:
            entry["node_ids"] = node_ids
        found.append(entry)
    return found


def _strip_git_suffix(path: str) -> str:
    path = unquote(path).strip().strip("/")
    if path.endswith(".git"):
        path = path[: -len(".git")]
    return path


def extract_gitlab_project_path(remote_or_url: str) -> str | None:
    value = remote_or_url.strip()
    http = urlparse(value)
    if http.scheme in {"http", "https"} and http.path:
        path = _strip_git_suffix(http.path)
        marker = "/-/merge_requests/"
        if marker in path:
            path = path.split(marker, 1)[0]
        return path or None
    ssh = GITLAB_SSH_RE.match(value)
    if ssh:
        return _strip_git_suffix(ssh.group(2)) or None
    return None


def extract_gitlab_mrs(text: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    seen: set[tuple[str | None, int]] = set()

    def add(iid: int, url: str | None, project_path: str | None) -> None:
        sig = (project_path, iid)
        if sig in seen:
            return
        seen.add(sig)
        entry: dict[str, Any] = {"iid": iid}
        if url:
            entry["url"] = url
        if project_path:
            entry["project_path"] = project_path
        found.append(entry)

    for match in GITLAB_MR_URL_RE.finditer(text):
        url = match.group(0).rstrip(").,];")
        iid = int(match.group(1))
        add(iid, url, extract_gitlab_project_path(url))

    for match in GITLAB_BANG_RE.finditer(text):
        add(int(match.group(2)), None, match.group(1))

    return found


def extract_gitlab_project_paths(text: str) -> list[str]:
    paths: list[str] = []
    for line in text.splitlines() or [text]:
        parsed = extract_gitlab_project_path(line.strip())
        if parsed:
            paths.append(parsed)
    for mr in extract_gitlab_mrs(text):
        path = mr.get("project_path")
        if isinstance(path, str):
            paths.append(path)
    return _unique(paths)


def extract_all(text: str) -> dict[str, Any]:
    mrs = extract_gitlab_mrs(text)
    figma = extract_figma(text)
    return {
        "jira_keys": extract_jira_keys(text),
        "figma": figma,
        "figma_node_ids": extract_figma_node_ids(text),
        "gitlab": {
            "mrs": mrs,
            "project_paths": extract_gitlab_project_paths(text),
        },
    }


def _run_self_test() -> int:
    cases: list[tuple[str, dict[str, Any]]] = [
        (
            "Ticket PROJ-123 and also ABC-9",
            {"jira_keys": ["PROJ-123", "ABC-9"]},
        ),
        (
            "see https://www.figma.com/design/AbCd12345/Login?node-id=1-2",
            {
                "figma": [
                    {
                        "file_key": "AbCd12345",
                        "node_ids": ["1:2"],
                    }
                ]
            },
        ),
        (
            "https://gitlab.example.com/group/app/-/merge_requests/42",
            {
                "gitlab": {
                    "mrs": [
                        {
                            "iid": 42,
                            "project_path": "group/app",
                        }
                    ],
                    "project_paths": ["group/app"],
                }
            },
        ),
        (
            "group/sub/app!7",
            {
                "gitlab": {
                    "mrs": [{"iid": 7, "project_path": "group/sub/app"}],
                    "project_paths": ["group/sub/app"],
                }
            },
        ),
        (
            "git@gitlab.example.com:acme/web.git",
            {"gitlab": {"project_paths": ["acme/web"]}},
        ),
        (
            "UTF-8 encoding is fine, real ticket is WEB-42",
            {"jira_keys": ["WEB-42"]},
        ),
        (
            "Spec node-id=85-1999 and metadata id=\"203:13054\" plus 203:11374",
            {"figma_node_ids": ["85:1999", "203:13054", "203:11374"]},
        ),
        (
            "Vide ESSA TELA without a node id",
            {"figma_node_ids": []},
        ),
    ]
    failed = 0
    for text, expected in cases:
        got = extract_all(text)
        for key, want in expected.items():
            if key == "gitlab":
                got_g = got["gitlab"]
                if "mrs" in want:
                    simplified = [
                        {k: mr[k] for k in ("iid", "project_path") if k in mr}
                        for mr in got_g["mrs"]
                    ]
                    if simplified != want["mrs"]:
                        failed += 1
                        print(f"FAIL mrs {text!r}\n  got {simplified}\n  want {want['mrs']}")
                if "project_paths" in want and got_g["project_paths"] != want["project_paths"]:
                    failed += 1
                    print(
                        f"FAIL project_paths {text!r}\n"
                        f"  got {got_g['project_paths']}\n"
                        f"  want {want['project_paths']}"
                    )
            elif key == "figma":
                simplified = [
                    {k: item[k] for k in item if k in {"file_key", "node_ids"}}
                    for item in got["figma"]
                ]
                if simplified != want:
                    failed += 1
                    print(f"FAIL figma {text!r}\n  got {simplified}\n  want {want}")
            elif key == "figma_node_ids":
                if got["figma_node_ids"] != want:
                    failed += 1
                    print(
                        f"FAIL figma_node_ids {text!r}\n"
                        f"  got {got['figma_node_ids']}\n"
                        f"  want {want}"
                    )
            elif got[key] != want:
                failed += 1
                print(f"FAIL {key} {text!r}\n  got {got[key]}\n  want {want}")
    if failed:
        print(f"{failed} check(s) failed")
        return 1
    print("OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract Jira keys, Figma URLs, and GitLab MR refs. No network."
    )
    parser.add_argument(
        "--text",
        help="Raw text to parse. If omitted, read stdin.",
    )
    parser.add_argument(
        "--file",
        help="Read text from this path. Use - for stdin.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in regex checks and exit.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return _run_self_test()

    if args.text is not None:
        text = args.text
    elif args.file:
        if args.file == "-":
            text = sys.stdin.read()
        else:
            with open(args.file, encoding="utf-8") as handle:
                text = handle.read()
    else:
        text = sys.stdin.read()

    json.dump(extract_all(text), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
