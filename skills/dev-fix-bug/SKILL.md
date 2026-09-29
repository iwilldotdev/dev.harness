---
name: dev-fix-bug
description: >-
  Minimal bug fix after a confirmed root cause: write fix-plan.md, Gate B-D,
  failing regression test on pre-fix commit (RED), smallest patch at the
  cause, GREEN plus proportional regression. One local commit. Three failed
  attempts stop. Product-scope growth reclassifies to Feature. No push.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Fix bug

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). Working tree + local commit. No push. A visual bug also loads [../dev-qa-guided-review/references/design-fidelity.md](../dev-qa-guided-review/references/design-fidelity.md) and applies the screen visual contract before UI.

1. `fix-plan.md`: cause, regression test, exact files, minimal change, risks, command. Visual bugs list the screen facts that change (fixed size, absolute position, complex style, copy).
2. **⛔ Gate B-D** — Write the Gate briefing in chat before the question (confirming, artifact path, summary of the minimal patch, confirm vs reject). Prompt verbatim `Gate B-D — Confirm minimal patch`. Does not authorize push. Do not re-ask facts already in intake `## Decisions`.
3. Regression test from the reproduction. Prove **RED** on the pre-fix commit (scratch/worktree).
4. Minimal patch at the source of the cause. No opportunistic refactor, new dependency, or “just in case”.
5. **GREEN** on the focused test + regression proportional to blast radius.
6. One concern / one commit (`check_commit.py`).
7. If the patch changes product or grows → stop and offer Feature.
8. Three failed attempts = hard stop (hypothesis/architecture). No automatic fourth try.

If `.dev/STATE.md` has `mode: agent`, do not ask at Gate B-D. Follow [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md): record the decision. Product-scope growth (resume `dev-feature-cycle`) and the third failure (resume `dev-debug`) still stop the cycle. The orchestrator loads the next skill.

## Close

Manual: the last line of the chat message is `Next skill: \`dev-verify-bug\`` after a green patch; `Next skill: \`dev-debug\`` after the third failed attempt, to revisit the hypothesis; `Next skill: \`dev-feature-cycle\`` when the patch would change product behavior. Agent mode does not emit this line.
