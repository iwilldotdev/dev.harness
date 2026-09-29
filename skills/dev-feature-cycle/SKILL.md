---
name: dev-feature-cycle
description: >-
  Feature-only orchestrator: loads one skill at a time from intake through
  specify, optional design/tasks, execute, independent verify, dual review,
  fix-reviews, and ship. Resumes from .dev/STATE.md. Use when the work is
  already a feature, or after dev-cycle delegates. Does not diagnose bugs
  as a default step.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Feature cycle

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). This skill **orchestrates**; it does not implement. Load **only** the current step’s skill — never the whole catalog.

Invoking this cycle directly **skips** Gate 0.

## Sequence

1. Resume: read `.dev/STATE.md`, reconcile with git (branch/status/commits) and artifacts. Current evidence wins. Present the next step **before** acting. If `mode: agent` is still set (an agent run interrupted before its stop), set `mode: manual` before the first step; from then on, every gate asks again.
2. `dev-feature-intake` → gap round, then Gate F-A.
3. `dev-specify` → Gate F-B. Spec is **never** skipped.
4. `dev-design` / `dev-tasks` — required if large **or** high-risk **or** UI with a screen. Skip only if F-A/F-B authorized small, normal risk, and no screen. A risk or screen the spec adds reverses that skip. The compact plan lives on the execute receipt.
5. `dev-execute` — fresh workers per batch (~5–7 tasks). Isolate with worktree/scratch, never stash. Workers do **not** push.
6. Task failure → `dev-debug` in `task-failure` mode (Gate F-X) and return to the **same** task. Do not create `.dev/bugs`. Do not switch to a Bug cycle.
7. `dev-verify-feature` — **fresh** context, author ≠ verifier. Max 3 execute↔verify loops. The third FAIL escalates to the user with `Next skill: none`.
8. `dev-mr-guided-review` → `dev-qa-guided-review` (chat-only).
9. Confirmed gaps → `dev-fix-reviews` (return `dev-execute`). Ship-ready ([`dev-ship` preconditions](../dev-ship/SKILL.md#preconditions)) → `dev-ship`. Any other verdict stays in review or `dev-fix-reviews`.
10. Finish only if `validate_state.py` passes.

Main session: gates, hyperlinks, state. Workers: heavy execute/verify. Effort matches risk. Do not pin a model version slug.

No-escalation: end the current skill and load the next with **its** allowlist.

## Close

Each finished manual step keeps the closing line that step defines (`Next skill: \`dev-...\``). This orchestrator does not replace that line. Agent mode is `dev-feature-agent`, invoked directly, not by this skill.
