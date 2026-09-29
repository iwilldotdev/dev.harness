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

**Manual mode:** consume **only** findings the user already confirmed from both reviews in the current conversation. Do **not** reconstruct the canonical report from memory. If the reports are not in this conversation, ask the user to paste them or re-run `dev-mr-guided-review` / `dev-qa-guided-review`.

**Agent mode:** consume findings with evidence from the MR and QA reports just emitted in the current conversation. Those recorded findings are confirmed for the autonomous correction loop; do not ask the user to confirm or paste them. If either report is absent, stop, explain what is missing, and name that review skill as the manual resume.

The current round contains only **new** issues. Do not reopen what already closed with evidence.

## Each issue in `reviews/round-NNN.md`

- Origin (`mr` | `qa`)
- Severity
- Evidence (`path:line`, **screen** node, CI job)
- `flow: feature|bug`
- Return: `dev-execute` (feature) | `dev-debug` (hypothesis) | `dev-fix-bug` (incomplete patch)

Visual GAP: reopen the **screen** `node-id` (`figma_get_design_context` + screenshot) **before** JSX. Apply the visual contract in [../dev-qa-guided-review/references/design-fidelity.md](../dev-qa-guided-review/references/design-fidelity.md): fixed size, absolute position, complex fill, effect, stroke, opacity, copy. Mismatch types include `fixed-size`, `absolute`, `effect`, `complex-fill`, `stroke`, `opacity`. No generic Modal/Drawer.

## Loop

1. Write the round (idempotent: do not duplicate `round-NNN.md`).
2. Run the correct return — do not inherit the next skill’s tools. A round with several returns runs them in flow order: `dev-debug` before `dev-fix-bug`, since a new hypothesis changes the patch. The closing line names the first.
3. Re-run the flow verifier (`dev-verify-feature` or `dev-verify-bug`) in a fresh context.
4. Re-run both reviews.
5. Max **three** rounds. Manual mode escalates to the user. Agent mode stops, explains the remaining gaps, and names the owning return skill; it does not ask another question.

After verifier and both reviews:

- Confirmed gaps remain → return to the owning skill. Manual mode names it in `Next skill:`. Agent mode loads it.
- Ship-ready ([`dev-ship` preconditions](../dev-ship/SKILL.md#preconditions)) in manual mode → `dev-ship`.
- Ship-ready in `mode: agent` → do **not** load `dev-ship`. Follow [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md): write `mode: manual`, the run log, and stop. The last line is `Next skill: \`dev-ship\``.
- `ADJUST`, `BLOCK`, an open Completeness row, or a receipt older than the last commit is not ship-ready. Continue the loop, or stop after three rounds.
- A review `INCOMPLETE` with no confirmed code gap is not a return to execute, debug, or fix-bug. It is the review `INCOMPLETE` blockage in [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md): stop and name that review. A third `INCOMPLETE` in a row stops the loop; do not start a fourth round.

## Close

Before the closing line, in chat: the path of `reviews/round-NNN.md`, each issue with its origin, severity, and return skill, and the round count out of three.

Manual: the last line of the chat message is `Next skill: \`dev-mr-guided-review\`` or `Next skill: \`dev-qa-guided-review\`` when that review is `INCOMPLETE` and the round has no confirmed code gap. Otherwise it is `Next skill: \`dev-execute\`` for a feature gap; `Next skill: \`dev-debug\`` for a wrong hypothesis; `Next skill: \`dev-fix-bug\`` for an incomplete patch. After that return, the flow continues at the verifier and both reviews. When the [`dev-ship` preconditions](../dev-ship/SKILL.md#preconditions) hold after that re-run, `Next skill: \`dev-ship\``. Agent mode does not emit this line between steps. On the `INCOMPLETE` stop, the agent still ends with that review skill, as in [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md).
