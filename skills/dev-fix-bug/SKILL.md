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

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). Working tree + local commit. No push.

1. `fix-plan.md`: cause, regression test, exact files, minimal change, risks, command.
2. **⛔ Gate B-D** — prompt verbatim `Gate B-D — Confirm minimal patch`. Does not authorize push.
3. Regression test from the reproduction. Prove **RED** on the pre-fix commit (scratch/worktree).
4. Minimal patch at the source of the cause. No opportunistic refactor, new dependency, or “just in case”.
5. **GREEN** on the focused test + regression proportional to blast radius.
6. One concern / one commit (`check_commit.py`).
7. If the patch changes product or grows → stop and offer Feature.
8. Three failed attempts = hard stop (hypothesis/architecture). No automatic fourth try.
