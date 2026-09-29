---
name: dev-debug
description: >-
  Scientific debugging via dev.mcp and git: root cause, change analysis,
  one falsifiable hypothesis. Read-only — does not patch. Bug mode writes
  investigation.md and hypothesis.md and stops at Gate B-C. Feature
  task-failure mode uses Gate F-X and returns to the same task without
  creating .dev/bugs. Use after reproduction (bug) or a failing feature task.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Debug (diagnosis)

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). **Does not patch.** MCP reads: pipelines/jobs, commit, contracts, ticket.

Iron law: no demonstrable cause, no patch.

## Method

Full error → recent changes (`git log`, pipelines) → data flow → working example → differences → **one** hypothesis with an observable prediction and a falsification test. Discarded hypotheses stay in the artifact with evidence.

Temporary instrumentation only in scratch/worktree; the real tree matches baseline afterwards.

## Modes

**`bug`:** write `investigation.md` + `hypothesis.md`. **⛔ Gate B-C** — Write the Gate briefing in chat before the question (confirming, artifact path, summary of cause and falsification, confirm vs reject). Prompt verbatim `Gate B-C — Confirm root cause`. No cause, do not advance. Do not re-ask facts already in intake `## Decisions`.

**`task-failure`:** diagnosis on the task receipt. **⛔ Gate F-X** — Write the Gate briefing in chat before the question. Prompt verbatim `Gate F-X — Confirm task diagnosis`. Return to the same task. Do not create `.dev/bugs`. Do not switch to a Bug cycle.

If `.dev/STATE.md` has `mode: agent`, do not ask. Follow [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md): record the decision, or stop when there is no demonstrable cause. The orchestrator loads the next skill.

## Close

Manual: in bug mode, the last line is `Next skill: \`dev-fix-bug\`` when Gate B-C confirmed a cause, and `Next skill: \`dev-debug\`` when there is no demonstrable cause. In task-failure mode, the last line is `Next skill: \`dev-execute\`` for the same task. Agent mode does not emit this line.
