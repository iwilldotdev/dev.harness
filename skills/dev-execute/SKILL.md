---
name: dev-execute
description: >-
  Implements a confirmed feature task against spec and Figma screen: tests
  derive from REQ outcomes, RED then minimal code, one local commit per task.
  UI requires opening the screen node-id first. Use after Gate F-D. On task
  failure, call dev-debug in task-failure mode — do not start a bug cycle.
  Local writes only; no push.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Execute (Feature)

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md) and [references/implement.md](references/implement.md).

Working tree + local commits. No push. MCP read-only.

## Contract

1. Load only spec, current design/task, decisions, and necessary code.
2. Tests derive from spec outcomes, not from the code. Record a RED failure before implementing new behavior.
3. Minimum for GREEN. Focused gate + regression proportional to risk. One atomic commit per task (`check_commit.py`).
4. **UI:** open the **screen** `node-id` (`figma_get_design_context` + screenshot) **before** JSX. Forbidden: generic Modal/Drawer, borrowed i18n, “equivalent flow”.
5. Intake/spec/design contradiction → return to the originating gate. No silent `SPEC_DEVIATION`.
6. Batches of ~5–7 tasks: fresh worker; worktree/scratch, never stash. Worker does not push.
7. Task failure → `dev-debug` in `task-failure` mode (Gate F-X). Do not create `.dev/bugs`. Do not turn this into a Bug cycle.
