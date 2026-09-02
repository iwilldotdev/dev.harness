---
name: dev-design
description: >-
  Technical design for a confirmed feature spec: files, contracts, callers,
  flags, failure modes, and Figma spec-vs-screen inventory with screen
  screenshots. Required for large or high-risk work and any UI with a Figma
  screen. Stops at Gate F-C. No placeholders. Use after dev-specify.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Design (Feature)

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md) and [../dev-qa-guided-review/references/design-fidelity.md](../dev-qa-guided-review/references/design-fidelity.md).

Required for large, high-risk, or UI with a Figma screen. Skip only if F-A/F-B authorized small+normal.

## Artifact `design.md`

- Spec vs **screen** inventory: fileKey, node-id, name, `spec|screen`, screenshot URL of the **screen**
- No screen frame: visual design = INCOMPLETE (not silent N/A)
- Files, responsibilities, flows, failures, flags, contracts (`gitlab_get_repository_file` only if cited)
- Tokens: `figma_get_variable_defs`; 403 → unknown, do not fake a design system
- No placeholders (“add validation”, TBD)

**⛔ Gate F-C** — prompt verbatim `Gate F-C — Confirm design`. Without confirmed screens, `dev-execute` must not mark UI as done.
