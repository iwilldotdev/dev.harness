---
name: dev-verify-bug
description: >-
  Independent bug verifier (author ≠ verifier): reproduce original symptom,
  confirm regression test RED on pre-fix commit and GREEN on HEAD, check
  cause not symptom, inspect diff scope. Writes validation.md. Failure
  returns to dev-debug (wrong hypothesis) or dev-fix-bug (incomplete patch).
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Verify Bug

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). Fresh context. Author ≠ verifier. No patch in this skill.

1. Reproduce the original symptom.
2. Scratch at the pre-fix commit: regression test **fails**. HEAD: **passes**.
3. Regressions + cause (not just symptom) + diff scope.
4. `validation.md`: reproduction, RED/GREEN, commands/results, `path:line`, diff range, PASS/FAIL/INCOMPLETE.

```bash
python3 "$SKILL_DIR/scripts/validate_bug.py" .dev/bugs/<slug>
```

Failure → `dev-debug` (hypothesis) or `dev-fix-bug` (patch), explicitly.
