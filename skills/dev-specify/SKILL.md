---
name: dev-specify
description: >-
  Writes a testable product spec from confirmed feature intake: REQ-NNN with
  EARS or when/then, expected outcomes, negatives, and origin evidence. Runs
  validate_spec.py. Stops at Gate F-B before design or code. Use after
  dev-feature-intake. Do not invent acceptance criteria. Not for bugs.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Specify (Feature)

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). Consumes `.dev/features/<slug>/intake.md`. No mass fetch; a punctual allowlist hole only if intake marks a gap.

## Artifact `spec.md`

- WHAT / WHY / WHO
- `REQ-NNN` requirements in EARS or when/then
- Each REQ points to a Jira field, frame/spec, or explicit gate decision
- Expected outcomes, negative errors/states, out of scope
- Do not complete ACs, invent copy, or treat a spec-sheet as a screen

```bash
python3 "$SKILL_DIR/scripts/validate_spec.py" .dev/features/<slug>/spec.md
```

Non-zero exit blocks.

**⛔ Gate F-B** — prompt verbatim `Gate F-B — Confirm requirements`. No confirmation, no design/code.
