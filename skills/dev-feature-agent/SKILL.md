---
name: dev-feature-agent
description: >-
  Agentic feature orchestrator: one intake gap round, then specify, design,
  tasks, execute, verify, dual review, and fix-reviews without further
  questions. Decides from intake decisions and surrounding evidence. Stops
  before dev-ship. Use when the user wants the feature cycle to run on its
  own. Does not replace the manual dev-feature-cycle.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Feature agent

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md) and [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md). This skill **orchestrates**; it does not implement. Load **only** the current step’s skill.

Set `.dev/STATE.md` `mode: agent` and `flow: feature` before the first step. Direct invocation skips Gate 0.

## Sequence

1. Resume: read `.dev/STATE.md`, reconcile with git and artifacts. Current evidence wins.
2. `dev-feature-intake` — gap round only when the ticket, Figma, git, or code leave a fact unresolved. That round is the **only** question. Record `## Decisions`. Then decide Gate F-A and continue.
3. `dev-specify` → decide Gate F-B. Spec is **never** skipped.
4. `dev-design` / `dev-tasks` — required if large **or** high-risk **or** UI with a screen. Decide after the spec: skip only when the intake classification **and** the spec both show small, normal risk, and no screen. A risk or screen the spec adds reverses an intake skip. Record that decision. Do not ask.
5. `dev-execute` — fresh workers per batch (~5–7 tasks). Isolate with worktree/scratch, never stash. Workers do **not** push.
6. Task failure → `dev-debug` in `task-failure` mode and return to the **same** task. Do not create `.dev/bugs`. Do not switch to a Bug cycle. Do not ask.
7. `dev-verify-feature` — **fresh** context, author ≠ verifier. Max 3 execute↔verify loops; then stop and explain.
8. `dev-mr-guided-review` → `dev-qa-guided-review`. Phase 1 of the MR review proceeds without asking.
9. Gaps with evidence → `dev-fix-reviews` (return `dev-execute`), then verifier and both reviews again. Max three rounds; then stop and explain.
10. Ship-ready (every [`dev-ship` precondition](../dev-ship/SKILL.md#preconditions) command exits 0, including `validation.md` PASS and a current readiness receipt): **stop before** loading `dev-ship`. Write `mode: manual`, the run log, and the Gate S briefing. Do not call remote writes.

A blockage in [agent-mode.md](../dev-shared/references/agent-mode.md) stops the cycle. Write `mode: manual` and the run log. Explain the blockage. The last line names the manual skill that resumes. Do not open another question round.

Do not emit `Next skill:` between steps. Load the next skill. The last line of the pre-ship stop is `Next skill: \`dev-ship\``; on a blockage it is `Next skill:` with the resume skill.

Main session owns state. Workers: heavy execute/verify. Effort matches risk. Do not pin a model version slug. No-escalation: end the current skill and load the next with **its** allowlist.

Before every stop, run `validate_state.py`; before the pre-ship stop, run every `dev-ship` precondition command. A failing result is a blockage, not a ship-ready stop. The pre-ship stop waits for the user to invoke `dev-ship`.
