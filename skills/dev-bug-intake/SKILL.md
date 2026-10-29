---
name: dev-bug-intake
description: >-
  Bug intake via dev.mcp: bind, resolve target, extract symptom expected vs
  actual, severity, blast radius, recent regressions, optional Figma screen
  if visual, and one gap round. Writes .dev/bugs/<slug>/intake.md. Stops at
  Gate B-A. Read-only. Do not use for features (use dev-feature-intake). Does
  not patch.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Bug intake

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). Read-only. No patch. A visual bug also loads [../dev-qa-guided-review/references/design-fidelity.md](../dev-qa-guided-review/references/design-fidelity.md).

Bind and target follow the same target discovery as QA (parser, remote, MR/branch, no hardcode). Ambiguity goes to the gap round. Read the ticket, Figma, git, and recent commits before asking. If the ticket is a child of DEV-8943, also read `.dev/features/dev-8943-gravacao-anotacoes/roadmap.md` and `jira-ship-comment.md`. The ship comment is part of every cycle of that epic.

Extract: symptom, expected × actual, environment, frequency, first/last known state, severity, blast radius, recent regression (commits/pipelines). A visual bug writes the same `visual-manifest.json` as a feature, saves the screen pack with `figma_fetch_screenshot`, and runs `figma_pack.py --check` plus `validate_intake.py` before Gate B-A. It does not depend on a feature `design.md`.

Classify: dev/staging/prod; functional/UI/integration/performance; reproducible/unknown; normal/high-risk.

## Gap round (once)

Before Gate B-A, list only facts those sources do not answer: ambiguous target, vague expected vs actual, unresolved screen on a visual bug, severity or environment absent from the ticket.

- No gap → do not ask.
- One or more gaps → one `gate-intake-gaps` form, as defined in [../dev-shared/references/gates.md](../dev-shared/references/gates.md#intake-gap-round). The briefing states what is already known; the form has one labeled question per gap. An ambiguous target is answered there, not by a separate Gate A round.
- Record each answer in `intake.md` under `## Decisions`.
- Later steps do not ask the same fact again.

In `mode: agent` this is the only question in the cycle. Gate B-A is then decided from those answers plus the evidence. Follow [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md).

Production incident: the harness **proposes** mitigation; rollback/deploy stay off the allowlist without explicit authorization.

**⛔ Gate B-A** — Write the Gate briefing in chat before the question (confirming, artifact path, summary of symptom and severity, confirm vs reject). Prompt verbatim `Gate B-A — Confirm symptom and severity`.

Artifact: `.dev/bugs/<slug>/intake.md`. `STATE.md` `flow: bug`. Empty field = `MISSING`. Include `## Decisions`.

## Close

Manual: the last line of the chat message is `Next skill: \`dev-reproduce-bug\``. Agent mode does not emit this line.
