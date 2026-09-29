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
- Visual contract table, one row per screen region: fixed size, hug/fill, absolute position, complex fill, effect, radius, stroke, opacity, text/copy. Numbers come from `nodes[]` (`visual`, `layout`, `fills`, `strokes`, `text`) plus the screen screenshot. No screen frame: `Visual design: INCOMPLETE` (not silent N/A). A resolved screen always gets the table
- Files, responsibilities, flows, failures, flags, contracts (`gitlab_get_repository_file` only if cited)
- Tokens: `figma_get_variable_defs`; 403 → unknown, do not fake a design system. A `boundVariables` id is the token; a raw `FIXED` value stays literal
- No placeholders (“add validation”, TBD)

```bash
python3 "$SKILL_DIR/scripts/validate_design.py" .dev/features/<slug>/design.md
```

Non-zero exit blocks. The script checks structure only: a design citing Figma has `## Visual contract` with the screen `node-id`, or declares `Visual design: INCOMPLETE`. Whether each row carries the right facts is checked by `dev-verify-feature` and QA against the screen.

**⛔ Gate F-C** — Write the Gate briefing in chat before the question (confirming, artifact path, summary, confirm vs reject). Prompt verbatim `Gate F-C — Confirm design`. Without confirmed screens, `dev-execute` must not mark UI as done. Do not re-ask facts already in intake `## Decisions`.

If `.dev/STATE.md` has `mode: agent`, do not ask. Follow [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md): record the decision. The orchestrator loads the next skill.

## Close

Manual: the last line of the chat message is `Next skill: \`dev-tasks\``. Agent mode does not emit this line.
