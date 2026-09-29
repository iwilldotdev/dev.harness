---
name: dev-verify-feature
description: >-
  Independent feature verifier (author ≠ verifier, fresh context): maps each
  REQ-NNN to outcome, test, and path:line; checks negatives, extra scope, RED
  baseline, Figma visual contract when UI, and a Completeness profile. Writes
  validation.md. FAIL without evidence. Use after the last feature task. Gaps
  return to dev-execute (max 3 loops).
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Verify Feature

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md) and, when the feature has UI, [../dev-qa-guided-review/references/design-fidelity.md](../dev-qa-guided-review/references/design-fidelity.md). Always **fresh** context. Author ≠ verifier. MCP read-only; do not “fix” code in this skill.

## Method

1. Re-run gates/tests.
2. Each `REQ-NNN` → outcome, test, `path:line`.
3. High-risk: failure/rollback/compatibility. UI: **screen** frame, cited states, and the visual contract (fixed size, absolute position, complex fill, effect, stroke, opacity, copy) against `path:line`.
4. Executable end-to-end flow (browser → API → state) if the surface exists; otherwise INCOMPLETE, do not infer.
5. `validation.md`: PASS / FAIL / INCOMPLETE, plus `## Completeness`. No evidence = FAIL.

## Completeness

One row per `REQ-NNN` and per visible UI surface:

| Item | Status | Evidence | Correction |
| --- | --- | --- | --- |
| REQ or surface | done / gap / not-checked | `path:line` or screen `node-id` | `dev-execute` or none |

`done` has evidence and no remaining defect. `gap` names the defect and `dev-execute`. `not-checked` is in scope but was not compared. PASS with an open `gap` is invalid.

```bash
python3 "$SKILL_DIR/scripts/validate_feature.py" .dev/features/<slug>/validation.md
```

Gaps → `dev-execute` on the first and second FAIL. On the third FAIL, escalate to the user. In `mode: agent`, the third FAIL stops the cycle with the blockage explained. Do not ask.

INCOMPLETE means verification could not run (no runtime, no reachable surface, no access). It is not a code gap: do not return to `dev-execute`. Name what is missing. In `mode: agent`, it is a blockage whose resume skill is `dev-verify-feature`.

## Close

Before the closing line, in chat: the path `.dev/features/<slug>/validation.md`, the verdict, and its `## Completeness` table as written.

Manual: the last line of the chat message is `Next skill: \`dev-mr-guided-review\`` when validation is PASS; `Next skill: \`dev-execute\`` when it is FAIL on the first or second execute↔verify iteration; `Next skill: none` when it is the third FAIL; `Next skill: \`dev-verify-feature\`` when it is INCOMPLETE, to re-run once the missing runtime, surface, or access is provided. Agent mode does not emit this line. In `mode: agent`, the third FAIL stops the cycle and explains the blockage.
