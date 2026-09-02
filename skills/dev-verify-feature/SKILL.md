---
name: dev-verify-feature
description: >-
  Independent feature verifier (author ≠ verifier, fresh context): maps each
  REQ-NNN to outcome, test, and path:line; checks negatives, extra scope, RED
  baseline, and Figma screen when UI. Writes validation.md. FAIL without
  evidence. Use after the last feature task. Gaps return to dev-execute
  (max 3 loops).
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Verify Feature

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). Always **fresh** context. Author ≠ verifier. MCP read-only; do not “fix” code in this skill.

## Method

1. Re-run gates/tests.
2. Each `REQ-NNN` → outcome, test, `path:line`.
3. High-risk: failure/rollback/compatibility. UI: **screen** frame + states.
4. Executable end-to-end flow (browser → API → state) if the surface exists; otherwise INCOMPLETE, do not infer.
5. `validation.md`: PASS / FAIL / INCOMPLETE. No evidence = FAIL.

```bash
python3 "$SKILL_DIR/scripts/validate_feature.py" .dev/features/<slug>/validation.md
```

Gaps → `dev-execute`. Max 3 iterations; then escalate to the user.
