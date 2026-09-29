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

**⛔ Gate B-B** — Write the Gate briefing in chat before the question (confirming, artifact path, summary of expected vs actual and the command result, confirm vs reject). Prompt verbatim `Gate B-B — Confirm reproduction`. Do not re-ask facts already in intake `## Decisions`.

- REPRODUCED → `dev-debug`
- NOT REPRODUCED → INCONCLUSIVE; ask for evidence in manual mode. Urgent mitigation only with explicit authorization **outside** this flow. No invented permanent patch.

If `.dev/STATE.md` has `mode: agent`, do not ask. A reproduced bug records `decision: proceed`. NOT REPRODUCED with no CI anchor stops the cycle: explain the blockage and name `dev-reproduce-bug` as the manual resume. Follow [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md).

## Close

Manual: the last line of the chat message is `Next skill: \`dev-debug\`` when REPRODUCED; `Next skill: \`dev-reproduce-bug\`` when NOT REPRODUCED (INCONCLUSIVE), stating that it runs again only with the new evidence listed above, and that without it the cycle ends here. Agent mode does not emit this line except on that blockage, where the resume skill is the same `dev-reproduce-bug`.
