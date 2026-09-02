---
name: dev-reproduce-bug
description: >-
  Reproduces a confirmed bug before any patch: minimal steps, safe data,
  command, expected vs actual, local run or CI job name(status) plus path/stack.
  Writes reproduction.md. Gate B-B: REPRODUCED advances; NOT REPRODUCED ends
  INCONCLUSIVE. Never invent a permanent fix. Read-only.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Reproduce bug

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). **No patch.**

Define minimal steps, safe data, environment, command, expected result. Reproduce locally **or** anchor on a CI job `name (failed)` + stack/`path:line` + commit. A failed pipeline without an observable scenario is **not** enough.

Artifact: `.dev/bugs/<slug>/reproduction.md` (baseline + stability).

**⛔ Gate B-B** — prompt verbatim `Gate B-B — Confirm reproduction`.

- REPRODUCED → `dev-debug`
- NOT REPRODUCED → INCONCLUSIVE; ask for evidence. Urgent mitigation only with explicit authorization **outside** this flow. No invented permanent patch.
