---
name: dev-fix-reviews
description: >-
  Closes confirmed gaps from dual reviews (MR + QA): writes round-NNN.md with
  only new confirmed issues, routes each back to the owning flow (feature
  execute or bug debug/fix), reopens Figma screen before UI, and re-runs
  verifier plus both reviews. Max three rounds. Does not post to MR or Jira.
  Use after reviews with confirmed findings.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Fix reviews

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). Working tree + local commits. MCP read-only. Do **not** post to MR/Jira.

## Source

Consume **only** findings the user already confirmed from both reviews in the current conversation. Do **not** reconstruct the canonical report from memory. If the reports are not in this conversation, ask the user to paste them or re-run `dev-mr-guided-review` / `dev-qa-guided-review`.

The current round contains only **new** issues. Do not reopen what already closed with evidence.

## Each issue in `reviews/round-NNN.md`

- Origin (`mr` | `qa`)
- Severity
- Evidence (`path:line`, **screen** node, CI job)
- `flow: feature|bug`
- Return: `dev-execute` (feature) | `dev-debug` (hypothesis) | `dev-fix-bug` (incomplete patch)

Visual GAP: reopen the **screen** `node-id` (`figma_get_design_context` + screenshot) **before** JSX. No generic Modal/Drawer.

## Loop

1. Write the round (idempotent: do not duplicate `round-NNN.md`).
2. Run the correct return — do not inherit the next skill’s tools.
3. Re-run the flow verifier (`dev-verify-feature` or `dev-verify-bug`) in a fresh context.
4. Re-run both reviews.
5. Max **three** rounds; then escalate to the user.

No confirmed gaps → `dev-ship`.
