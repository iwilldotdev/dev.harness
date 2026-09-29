---
name: dev-execute
description: >-
  Implements a confirmed feature task against spec and the Figma screen visual
  contract: tests derive from REQ outcomes, RED then minimal code, one local
  commit per task. UI requires opening the screen node and applying fixed
  values and complex styles before JSX. Use after Gate F-D. On task failure,
  call dev-debug in task-failure mode — do not start a bug cycle. Local writes
  only; no push.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Execute (Feature)

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md), [references/implement.md](references/implement.md), and [../dev-qa-guided-review/references/design-fidelity.md](../dev-qa-guided-review/references/design-fidelity.md).

Working tree + local commits. No push. MCP read-only.

## Contract

1. Load only spec, current design/task, decisions, and necessary code.
2. Tests derive from spec outcomes, not from the code. Record a RED failure before implementing new behavior.
3. Minimum for GREEN. Focused gate + regression proportional to risk. One atomic commit per task (`check_commit.py`).
4. **UI:** open the **screen** `node-id` (`figma_get_design_context` + screenshot) **before** JSX. Apply the visual contract in `design.md` or, when design was skipped, the screen node’s `visual`, `layout`, `fills`, `strokes`, and `text`. The task receipt lists each applied value (fixed size, absolute position, complex fill, effect, stroke, opacity, copy). Forbidden: generic Modal/Drawer, borrowed i18n, “equivalent flow”.
5. Intake/spec/design contradiction → return to the originating gate. No silent `SPEC_DEVIATION`.
6. Batches of ~5–7 tasks: fresh worker; worktree/scratch, never stash. Worker does not push.
7. Task failure → `dev-debug` in `task-failure` mode (Gate F-X). Do not create `.dev/bugs`. Do not turn this into a Bug cycle.

If `.dev/STATE.md` has `mode: agent`, a task-failure gate is decided by [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md). Do not ask.

## Close

Before the closing line, in chat: each task done with its commit SHA, the receipt summary (tests run and, for UI, the visual-contract values applied), and any task still red.

Manual: the last line of the chat message is `Next skill: \`dev-verify-feature\`` when the task batch is green; `Next skill: \`dev-debug\`` in task-failure mode when a task fails. Agent mode does not emit this line.
