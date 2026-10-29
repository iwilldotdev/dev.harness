#!/usr/bin/env python3
"""Validate feature spec.md. No network."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQ = re.compile(r"REQ-\d+")
WHEN = re.compile(r"(when |if |the system shall|ears|quando |então|then )", re.I)
PLACEHOLDERS = ("TODO", "TBD", "lorem ipsum", "xxx")
ORIGIN = re.compile(r"(jira|gate|figma|intake|field|description|ac\b)", re.I)
SCOPE = re.compile(r"(out of scope|fora de escopo|scope)", re.I)
RISK = re.compile(r"(risk|risco)", re.I)
OUTCOME = re.compile(r"(outcome|expected|então|then the)", re.I)
UI_REF = re.compile(r"(figma|node-id)", re.I)
VISUAL = re.compile(r"^## Visual contract\b[^\n]*\n(.*?)(?=^## |\Z)", re.M | re.S)
NODE_ID = re.compile(r"\b\d+[:-]\d+\b")
# UI surface vocabulary inside a REQ paragraph. Deliberately excludes DB words
# ("tabela", "coluna", "endpoint") to avoid flagging data-model REQs.
UI_VOCAB = re.compile(
    r"\b(tela|screen|modal|botão|botao|button|card|drawer|popover|tooltip|"
    r"dropdown|menu lateral|breadcrumb|rodapé|rodape|footer|checkbox|sidebar|"
    r"anexar à tela|tela nova)\b",
    re.I,
)
HEADING = re.compile(r"^#{1,6}\s", re.M)


def _sections(text: str) -> list[str]:
    parts = HEADING.split(text)
    return [part for part in parts if part.strip()]


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing {path}"]
    text = path.read_text(encoding="utf-8")
    ids = REQ.findall(text)
    if not ids:
        errors.append("no REQ-NNN identifiers")
    if len(ids) != len(set(ids)):
        errors.append("duplicate REQ ids")
    if not WHEN.search(text):
        errors.append("requirements must be testable (EARS or when/then)")
    if not ORIGIN.search(text):
        errors.append("each spec must cite origin evidence (Jira/gate/intake/Figma)")
    if not SCOPE.search(text):
        errors.append("spec must declare out of scope")
    if not RISK.search(text):
        errors.append("spec must declare risk")
    if not OUTCOME.search(text):
        errors.append("spec must declare expected outcomes")
    visual = VISUAL.search(text)
    if UI_REF.search(text):
        if not visual:
            errors.append("UI spec that cites Figma must include Visual contract")
        elif not NODE_ID.search(visual.group(1)):
            errors.append("Visual contract must cite the screen node-id")
    if visual:
        rest = text[: visual.start()] + text[visual.end() :]
        for node_id in {match.group(0) for match in NODE_ID.finditer(visual.group(1))}:
            normalized_dash = node_id.replace(":", "-")
            if node_id not in rest and normalized_dash not in rest:
                errors.append(
                    f"Visual contract screen {node_id} is not cited by any requirement"
                )
        for section in _sections(text[: visual.start()]):
            if not REQ.search(section) or not UI_VOCAB.search(section):
                continue
            if NODE_ID.search(section):
                continue
            errors.append(
                "UI requirement section must cite the screen node-id "
                f"(section starting {section.strip().splitlines()[0][:60]!r})"
            )
    for token in PLACEHOLDERS:
        if token.lower() in text.lower():
            errors.append(f"placeholder {token}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args(argv)
    errors = validate(Path(args.path))
    if errors:
        print("FAIL")
        for err in errors:
            print(err)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
