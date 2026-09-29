---
name: dev-bug-agent
description: >-
  Agentic bug orchestrator: one intake gap round, then reproduce, debug,
  minimal fix, verify, dual review, and fix-reviews without further questions.
  Decides from intake decisions and surrounding evidence. Stops before
  dev-ship. Never enters specify, design, tasks, or execute. Use when the
  user wants the bug cycle to run on its own.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Bug agent

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md) and [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md). Orchestrates; does not implement. Load **only** the current step’s skill.

Set `.dev/STATE.md` `mode: agent` and `flow: bug` before the first step. Direct invocation skips Gate 0.

Do **not** use `dev-specify`, `dev-design`, `dev-tasks`, or `dev-execute`. If investigation reveals new behavior, a product decision, or a redesign: **stop** and name `dev-feature-cycle`. Do not invent the product change.

## Sequence

1. Resume via `.dev/STATE.md` + git + artifacts.
2. `dev-bug-intake` — gap round only for facts the ticket, Figma, git, and code do not answer. That round is the **only** question. Record `## Decisions`. Then decide Gate B-A and continue.
3. `dev-reproduce-bug`. REPRODUCED → continue. NOT REPRODUCED with no CI anchor → stop, explain, name `dev-reproduce-bug`. No invented permanent patch.
4. `dev-debug` in `bug` mode. No demonstrable cause → stop and explain. Do not ask.
5. `dev-fix-bug`. One fixer. Three attempts = hard stop. Decide Gate B-D from the hypothesis and the plan. Do not ask.
6. `dev-verify-bug` — **separate** verifier, fresh context. Failure → `dev-debug` (hypothesis) or `dev-fix-bug` (patch), explicitly. Do not ask.
7. `dev-mr-guided-review` → `dev-qa-guided-review`. Bug with no UI/AC: dimensions become N/A through the recorded decision, never silently skipped.
8. Gaps with evidence → `dev-fix-reviews` (return `dev-debug` or `dev-fix-bug`), then verifier and both reviews. Max three rounds; then stop and explain.
9. Ship-ready (every [`dev-ship` precondition](../dev-ship/SKILL.md#preconditions) command exits 0, including `validation.md` PASS and a current readiness receipt): **stop before** loading `dev-ship`. Write `mode: manual`, the run log, and the Gate S briefing. Do not call remote writes.

A blockage in [agent-mode.md](../dev-shared/references/agent-mode.md) stops the cycle. Write `mode: manual` and the run log. Explain the blockage. The last line names the manual skill that resumes. Do not open another question round.

Do not emit `Next skill:` between steps. Load the next skill. The last line of the pre-ship stop is `Next skill: \`dev-ship\``; on a blockage it is `Next skill:` with the resume skill.

Production/high-risk: wider triage, **proposed** mitigation (not executed without authorization), optional postmortem. Rigor increases; the patch stays minimal.

Before every stop, run `validate_state.py`; before the pre-ship stop, run every `dev-ship` precondition command. A failing result is a blockage, not a ship-ready stop. The pre-ship stop waits for the user to invoke `dev-ship`.

Effort matches risk. Do not pin a model version slug. Do not escalate allowlists between skills.
