#!/usr/bin/env python3
"""Validate skill packages: name=folder, prefix, links, sections, allowlists. No network."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

REQUIRED_SKILLS = (
    "dev-shared",
    "dev-cycle",
    "dev-feature-cycle",
    "dev-feature-agent",
    "dev-feature-intake",
    "dev-specify",
    "dev-design",
    "dev-tasks",
    "dev-execute",
    "dev-verify-feature",
    "dev-bug-cycle",
    "dev-bug-agent",
    "dev-bug-intake",
    "dev-reproduce-bug",
    "dev-debug",
    "dev-fix-bug",
    "dev-verify-bug",
    "dev-mr-guided-review",
    "dev-qa-guided-review",
    "dev-fix-reviews",
    "dev-ship",
)

READ_ONLY = {
    "dev-cycle",
    "dev-feature-cycle",
    "dev-feature-agent",
    "dev-bug-cycle",
    "dev-bug-agent",
    "dev-feature-intake",
    "dev-bug-intake",
    "dev-specify",
    "dev-design",
    "dev-tasks",
    "dev-reproduce-bug",
    "dev-debug",
    "dev-verify-feature",
    "dev-verify-bug",
    "dev-mr-guided-review",
    "dev-qa-guided-review",
    "dev-shared",
}

WRITE_TOOLS = (
    "gitlab_save_merge_request",
    "gitlab_create_merge_request_note",
    "gitlab_accept_merge_request",
    "gitlab_add_branch",
    "gitlab_add_commit",
    "gitlab_create_issue",
    "jira_create_issue",
    "jira_edit_issue",
    "jira_transition_issue",
    "jira_add_comment",
    "jira_add_worklog",
    "jira_create_issue_link",
    "jira_create_remote_issue_link",
    "confluence_create_page",
    "confluence_update_page",
    "confluence_create_footer_comment",
    "confluence_create_inline_comment",
)

NEVER_ACCEPT = "gitlab_accept_merge_request"

HOST_LEAK = re.compile(
    r"\b(cursor|getdynamictools|calldynamictool|askquestion)\b",
    re.I,
)
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SECRET = re.compile(
    r"(glpat-[A-Za-z0-9_-]{20,}|figd_[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,})"
)
NEGATION = re.compile(
    r"\b(never|do not|don't|forbidden|denylist|absolute denylist|"
    r"not call|without|except)\b",
    re.I,
)
NAME_RE = re.compile(r"^dev-[a-z0-9-]+$")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data: dict[str, str] = {}
    key: str | None = None
    for line in parts[1].splitlines():
        if key and (line.startswith("  ") or line.startswith("\t")):
            data[key] = (data[key] + " " + line.strip()).strip()
            continue
        if ":" in line and not line.startswith(" "):
            raw_key, raw_val = line.split(":", 1)
            key = raw_key.strip()
            data[key] = raw_val.strip().lstrip(">-").strip()
    return data


def write_tool_violations(text: str, skill: str) -> list[str]:
    errors: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for tool in WRITE_TOOLS:
            if not re.search(rf"`{re.escape(tool)}`|\b{re.escape(tool)}\b", line):
                continue
            listed = re.sub(r"^[\s>*-]+", "", line).strip().strip("`")
            if listed == tool:
                continue
            if skill in READ_ONLY and not NEGATION.search(line):
                errors.append(f"{skill}:{lineno} read-only skill mentions {tool} without negation")
            if tool == NEVER_ACCEPT and skill == "dev-ship" and not NEGATION.search(line):
                errors.append(f"{skill}:{lineno} must not instruct {tool}")
            if skill in {"dev-execute", "dev-fix-bug", "dev-fix-reviews"} and not NEGATION.search(
                line
            ):
                errors.append(f"{skill}:{lineno} local-write skill must not call MCP write {tool}")
    return errors


def check_links(skill_dir: Path, text: str, rel: str) -> list[str]:
    errors: list[str] = []
    base = (skill_dir / rel).parent
    for match in MD_LINK.finditer(text):
        href = match.group(1).split("#", 1)[0].split(" ", 1)[0]
        if not href or href.startswith(("http://", "https://", "mailto:")):
            continue
        target = (base / href).resolve()
        if not target.exists():
            errors.append(f"{rel}: broken link {href}")
    return errors


def check_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{name}: missing SKILL.md"]
    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm.get("name") != name:
        errors.append(f"{name}: frontmatter name {fm.get('name')!r} != folder")
    if not NAME_RE.match(name):
        errors.append(f"{name}: folder must be dev-<step>")
    if "description" not in fm:
        errors.append(f"{name}: missing description")
    compat = fm.get("compatibility", "")
    if "dev.mcp" not in compat:
        errors.append(f"{name}: compatibility must mention dev.mcp")
    if "cursor" in compat.lower():
        errors.append(f"{name}: compatibility must not name a specific host")
    disable = fm.get("disable-model-invocation", "")
    if name == "dev-cycle":
        if disable.lower() in {"true", "yes"}:
            errors.append("dev-cycle must omit disable-model-invocation")
    elif disable.lower() != "true":
        errors.append(f"{name}: disable-model-invocation must be true")
    if name != "dev-shared" and "../dev-shared/SKILL.md" not in text:
        errors.append(f"{name}: must load ../dev-shared/SKILL.md")
    if not re.search(r"^# ", text, re.M):
        errors.append(f"{name}: missing heading")
    errors.extend(write_tool_violations(text, name))
    if HOST_LEAK.search(text):
        errors.append(f"{name}: must not name a specific host or host-only tools")
    errors.extend(check_links(skill_dir, text, "SKILL.md"))
    for extra in skill_dir.rglob("*.md"):
        if extra.name == "SKILL.md":
            continue
        rel = extra.relative_to(skill_dir).as_posix()
        body = extra.read_text(encoding="utf-8")
        errors.extend(check_links(skill_dir, body, rel))
        errors.extend(write_tool_violations(body, name))
        if HOST_LEAK.search(body):
            errors.append(f"{name}/{rel}: must not name a specific host or host-only tools")
    return errors


def scan_secrets(root: Path) -> list[str]:
    errors: list[str] = []
    skip = {".git", "tests", "__pycache__"}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".py", ".yml", ".yaml"}:
            continue
        if any(part in skip for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if SECRET.search(text):
            errors.append(f"{path.relative_to(root)}: secret-like token")
    return errors


def validate(root: Path | None = None) -> list[str]:
    root = root or ROOT
    skills = root / "skills"
    errors: list[str] = []
    found = sorted(p.name for p in skills.iterdir() if p.is_dir() and p.name.startswith("dev-"))
    for name in REQUIRED_SKILLS:
        if name not in found:
            errors.append(f"missing skill {name}")
    extra = set(found) - set(REQUIRED_SKILLS)
    for name in sorted(extra):
        errors.append(f"unexpected skill {name}")
    for name in found:
        errors.extend(check_skill(skills / name))
    errors.extend(scan_secrets(root))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args(argv)
    errors = validate(Path(args.root))
    if errors:
        print("FAIL")
        for err in errors:
            print(err)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
