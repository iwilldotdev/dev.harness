---
name: dev-specify
description: >-
  Writes a testable product spec from confirmed feature intake: REQ-NNN with
  EARS or when/then, expected outcomes, negatives, and origin evidence. UI
  requirements cite the Figma screen visual contract. Runs validate_spec.py.
  Stops at Gate F-B before design or code. Use after dev-feature-intake. Do
  not invent acceptance criteria. Not for bugs.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Specify (Feature)

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md) and [../dev-qa-guided-review/references/design-fidelity.md](../dev-qa-guided-review/references/design-fidelity.md). Consumes `.dev/features/<slug>/intake.md`. No mass fetch; a punctual allowlist hole only if intake marks a gap.

## Artifact `spec.md`

- WHAT / WHY / WHO
- `REQ-NNN` requirements in EARS or when/then
- Each REQ points to a Jira field, frame/spec, or explicit gate decision
- Expected outcomes, negative errors/states, out of scope
- Do not complete ACs, invent copy, or treat a spec-sheet as a screen
- UI: each visual REQ cites the **screen** `node-id` and the testable facts from the visual contract (fixed measure, complex style, literal copy). Add `## Visual contract`. A spec-sheet is not a visual requirement.

```bash
python3 "$SKILL_DIR/scripts/validate_spec.py" .dev/features/<slug>/spec.md
```

Non-zero exit blocks.

**⛔ Gate F-B** — Write the Gate briefing in chat before the question (confirming, artifact path, summary, confirm vs reject). Prompt verbatim `Gate F-B — Confirm requirements`. No confirmation, no design/code. Do not re-ask facts already in intake `## Decisions`.

If `.dev/STATE.md` has `mode: agent`, do not ask. Follow [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md): record the decision. The orchestrator loads the next skill.

## Close

Manual: the last line of the chat message is `Next skill: \`dev-design\`` when the work is large, high-risk, or UI with a screen, including when the spec adds a screen or a higher risk after an intake skip. `Next skill: \`dev-execute\`` only when F-A/F-B authorized a skip and both the intake and the spec are small, normal risk, and have no screen. Agent mode does not emit this line.
