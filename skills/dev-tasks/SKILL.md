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
- Zero TBD / “similar to Task N”

```bash
python3 "$SKILL_DIR/scripts/validate_tasks.py" .dev/features/<slug>/tasks.md
```

**⛔ Gate F-D** — prompt verbatim `Gate F-D — Confirm execution`. Approval does **not** authorize push.
