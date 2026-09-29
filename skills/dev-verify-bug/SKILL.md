---
name: dev-verify-bug
description: >-
  Independent bug verifier (author ≠ verifier): reproduce original symptom,
  confirm regression test RED on pre-fix commit and GREEN on HEAD, check
  cause not symptom, inspect diff scope, and write a Completeness profile.
  Writes validation.md. Failure returns to dev-debug (wrong hypothesis) or
  dev-fix-bug (incomplete patch).
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Verify Bug

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). Fresh context. Author ≠ verifier. No patch in this skill.

1. Reproduce the original symptom.
2. Scratch at the pre-fix commit: regression test **fails**. HEAD: **passes**.
3. Regressions + cause (not just symptom) + diff scope. Visual bugs: screen visual contract against the diff.
4. `validation.md`: reproduction, RED/GREEN, commands/results, `path:line`, diff range, PASS/FAIL/INCOMPLETE, plus `## Completeness`.

## Completeness

One row for the symptom and one for the cause:

| Item | Status | Evidence | Correction |
| --- | --- | --- | --- |
| symptom or cause | done / gap / not-checked | `path:line` or command result | `dev-debug` / `dev-fix-bug` / none |

`done` means the cause is fixed and the original symptom no longer reproduces. `gap` names what is still wrong. PASS with an open `gap` is invalid.

```bash
python3 "$SKILL_DIR/scripts/validate_bug.py" .dev/bugs/<slug>
```

Failure → `dev-debug` (hypothesis) or `dev-fix-bug` (patch), explicitly. In `mode: agent`, do not ask; the orchestrator loads that return. Follow [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md).

INCOMPLETE means verification could not run (no runtime, no pre-fix scratch, no access). It is not a failed patch: do not return to `dev-debug` or `dev-fix-bug`. Name what is missing. In `mode: agent`, it is a blockage whose resume skill is `dev-verify-bug`.

## Close

Before the closing line, in chat: the path `.dev/bugs/<slug>/validation.md`, the verdict, and its `## Completeness` table as written.

Manual: the last line of the chat message is `Next skill: \`dev-mr-guided-review\`` when PASS; `Next skill: \`dev-debug\`` when the hypothesis is wrong; `Next skill: \`dev-fix-bug\`` when the patch is incomplete; `Next skill: \`dev-verify-bug\`` when INCOMPLETE, to re-run once what is missing is provided. Agent mode does not emit this line.
