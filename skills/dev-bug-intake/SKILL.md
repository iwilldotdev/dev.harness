---
name: dev-bug-intake
description: >-
  Bug intake via dev.mcp: bind, resolve target, extract symptom expected vs
  actual, severity, blast radius, recent regressions, and optional Figma screen
  if visual. Writes .dev/bugs/<slug>/intake.md. Stops at Gate B-A. Read-only.
  Do not use for features (use dev-feature-intake). Does not patch.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Bug intake

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). Read-only. No patch.

Bind and target follow the same Gate A as QA (parser, remote, MR/branch, no hardcode).

Extract: symptom, expected × actual, environment, frequency, first/last known state, severity, blast radius, recent regression (commits/pipelines). UI: **screen** frame only if the bug is visual.

Classify: dev/staging/prod; functional/UI/integration/performance; reproducible/unknown; normal/high-risk.

Production incident: the harness **proposes** mitigation; rollback/deploy stay off the allowlist without explicit authorization.

**⛔ Gate B-A** — prompt verbatim `Gate B-A — Confirm symptom and severity`.

Artifact: `.dev/bugs/<slug>/intake.md`. `STATE.md` `flow: bug`.
