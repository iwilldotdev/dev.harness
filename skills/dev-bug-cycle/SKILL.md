---
name: dev-bug-cycle
description: >-
  Bug-only orchestrator: intake, reproduce, scientific debug, minimal fix,
  independent verify, dual review, fix-reviews, and ship. Never enters
  specify/design/tasks/execute. Stops and offers Feature reclassification if
  the investigation reveals new product behavior. Use when the work is already
  a bug, or after dev-cycle delegates.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Bug cycle

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). Orchestrates; does not implement. Load **only** the current step’s skill.

Invoking this cycle directly **skips** Gate 0.

Do **not** use `dev-specify`, `dev-design`, `dev-tasks`, or `dev-execute`. If investigation reveals new behavior, a product decision, or a redesign: **stop** and offer Feature.

## Sequence

1. Resume via `.dev/STATE.md` + git + artifacts. Next step in chat before acting.
2. `dev-bug-intake` → Gate B-A.
3. `dev-reproduce-bug` → Gate B-B. NOT REPRODUCED = INCONCLUSIVE; no invented permanent patch.
4. `dev-debug` in `bug` mode → Gate B-C. No demonstrable cause, do not advance.
5. `dev-fix-bug` → Gate B-D. One fixer. Three attempts = hard stop.
6. `dev-verify-bug` — **separate** verifier, fresh context. Failure → `dev-debug` (hypothesis) or `dev-fix-bug` (patch), explicitly.
7. `dev-mr-guided-review` → `dev-qa-guided-review`. Bug with no UI/AC: dimensions become N/A through QA gates, never silently skipped.
8. Gaps → `dev-fix-reviews` (return `dev-debug` or `dev-fix-bug`). No gaps → `dev-ship`.
9. Finish only if `validate_state.py` passes.

Production/high-risk: wider triage, **proposed** mitigation (not executed without authorization), optional postmortem. Rigor increases; the patch stays minimal.

Effort matches risk. Do not pin a model version slug. Do not escalate allowlists between skills.
