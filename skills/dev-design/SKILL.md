---
name: dev-design
description: >-
  Technical design for a confirmed feature spec: files, contracts, callers,
  flags, failure modes, and a Figma visual contract per screen region with
  fixed sizes and complex styles. Required for large or high-risk work and
  any UI with a Figma screen. Stops at Gate F-C. No placeholders. Use after
  dev-specify.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Design (Feature)

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md) and [../dev-qa-guided-review/references/design-fidelity.md](../dev-qa-guided-review/references/design-fidelity.md).

Required for large, high-risk, or UI with a Figma screen. Skip only if F-A/F-B authorized small+normal.

## Artifact `design.md`

- Spec vs **screen** inventory: fileKey, node-id, name, `spec|screen`, screenshot URL of the **screen**
- Visual contract table, one row per screen region: fixed size, hug/fill, absolute position, complex fill, effect, radius, stroke, opacity, text/copy. Numbers come from the **Figma pack** (`figma/<node-id>.json` — the persisted `nodes[]`: `visual`, `layout`, `fills`, `strokes`, `text`) plus the screen screenshot in `figma/`. Every row needs a node-id **and** at least one concrete fact (measure, hex color, or literal copy) — `validate_design.py` enforces it. A screen fetched for the table is saved into the pack; run `figma_pack.py --check` before the gate. No screen frame: `Visual design: INCOMPLETE` (not silent N/A). A resolved screen always gets the table
- Files, responsibilities, flows, failures, flags, contracts (`gitlab_get_repository_file` only if cited)
- Tokens: do not call `figma_get_variable_defs`. Variable definitions are optional. A 403 or a missing variables payload is not unknown and is not `Visual design: INCOMPLETE`. Use the literal values on the node and the screenshot. A `boundVariables` id does not replace that literal
- No placeholders (“add validation”, TBD)

```bash
python3 "$SKILL_DIR/scripts/validate_design.py" .dev/features/<slug>/design.md
python3 "$(dirname "$SKILL_DIR")/dev-shared/scripts/figma_pack.py" .dev/features/<slug> --check
```

Non-zero exit blocks. `validate_design.py` checks structure **and** row content now: each Visual contract row must cite the screen `node-id` and carry a measure/hex/copy fact. `figma_pack.py --check` fails while any cited screen lacks its pack JSON or PNG. Whether each row carries the right facts is still checked by `dev-verify-feature` and QA against the screen.

**⛔ Gate F-C** — Write the Gate briefing in chat before the question (confirming, artifact path, summary, confirm vs reject). Prompt verbatim `Gate F-C — Confirm design`. Without confirmed screens, `dev-execute` must not mark UI as done. Do not re-ask facts already in intake `## Decisions`.

If `.dev/STATE.md` has `mode: agent`, do not ask. Follow [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md): record the decision. The orchestrator loads the next skill.

## Close

Manual: the last line of the chat message is `Next skill: \`dev-tasks\``. Agent mode does not emit this line.
