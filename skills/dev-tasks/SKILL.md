---
name: dev-tasks
description: >-
  Breaks a confirmed feature design into atomic tasks with exact files,
  interfaces, REQ-NNN coverage, RED/GREEN tests, and observable gates. Runs
  validate_tasks.py. Stops at Gate F-D. Approving tasks does not authorize
  push. Use after dev-design (or compact plan if skip was authorized).
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Tasks (Feature)

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). One task = one test cycle + one commit.

## Each task

- Create/Modify/Test paths
- Interfaces Consumes / Produces
- Covered `REQ-NNN`, `Depends on`
- RED/GREEN test with a **command** and an observable gate
- User-facing feature: UAT/E2E scenario if the repo has a runtime; do not substitute static inspection
- UI task: names the screen `node-id` and the visual-contract facts it must land (fixed size, absolute position, complex style, copy). `dev-verify-feature` and QA check them against the screen; the script does not
- Zero TBD / “similar to Task N”

```bash
python3 "$SKILL_DIR/scripts/validate_tasks.py" .dev/features/<slug>/tasks.md
```

**⛔ Gate F-D** — Write the Gate briefing in chat before the question (confirming, artifact path, summary, confirm vs reject). Prompt verbatim `Gate F-D — Confirm execution`. Approval does **not** authorize push. Do not re-ask facts already in intake `## Decisions`.

If `.dev/STATE.md` has `mode: agent`, do not ask. Follow [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md): record the decision. The orchestrator loads the next skill.

## Close

Manual: the last line of the chat message is `Next skill: \`dev-execute\``. Agent mode does not emit this line.
