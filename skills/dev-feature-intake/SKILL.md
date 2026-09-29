---
name: dev-feature-intake
description: >-
  Feature intake via dev.mcp: bind server, resolve GitLab target, extract Jira
  and Figma (spec vs screen, visual contract), classify complexity and risk,
  ask one gap round, and write .dev/features/<slug>/intake.md. Use at the
  start of a feature. Stops at Gate F-A. Read-only. Do not use for bugs (use
  dev-bug-intake).
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Feature intake

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md) and [../dev-qa-guided-review/references/design-fidelity.md](../dev-qa-guided-review/references/design-fidelity.md). MCP read-only. Do not invent ACs.

```
Step 0 Bind → target (parser + git + MR) → read Jira/Figma/CI and code
  → gap round → Gate F-A → intake.md
```

## Steps

1. Bind `dev.mcp`. Smoke `gitlab_whoami`. `figma_whoami` if a Figma URL is present.
2. User text → `extract_refs.py`. Remote `origin` → `projectId`. Current branch. No IID: `gitlab_list_merge_requests` (`state: opened`, `sourceBranch`). Do not invent an IID. Branch mode: merge-base.
3. After the target is readable: `jira_get_issue` + `jira_get_remote_issue_links`. Figma: `figma_get_design_context` + `figma_get_metadata` on each node, then the screen hop in design-fidelity.md. Capture the visual contract (fixed size, absolute position, complex fill, effect, stroke, opacity, copy) for each **screen**. Confluence only if linked and Jira has no AC/Figma.
4. Read-only grounding: patterns, contracts, tests, docs. Verification surface (unit/API/browser/state). Do **not** propose architecture yet.
5. Classify complexity (small/medium/large) and risk (normal/high) with evidence. Skip design/tasks only if small, normal risk, and no screen — propose that at Gate F-A, do not decide alone in manual mode. A screen, a large size, or high risk is not a skip.

## Gap round (once)

Before Gate F-A, list only facts the ticket, Figma, git, and code do not answer: ambiguous target (0 / many MRs, several projects, ambiguous base), missing AC, unresolved screen frame.

- No gap → do not ask.
- One or more gaps → one `gate-intake-gaps` form, as defined in [../dev-shared/references/gates.md](../dev-shared/references/gates.md#intake-gap-round). The briefing states what is already known; the form has one labeled question per gap.
- Record each answer in `intake.md` under `## Decisions`.
- Later steps read `## Decisions` and do not ask the same fact again.

In `mode: agent` this is the only question in the cycle. Gate F-A is then decided from those answers plus the evidence. Follow [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md).

**⛔ Gate F-A** — Write the Gate briefing in chat before the question (confirming, artifact path, summary of target, Jira, spec vs screen, risk, proposed skip, confirm vs reject). Prompt verbatim `Gate F-A — Confirm context`. An ambiguous target is resolved by the `Target MR` / `Merge-base` questions of the gap round, not by a separate Gate A round.

Artifact: `.dev/features/<slug>/intake.md` (keys, fileKey, spec **and** screen node-id, visual-contract notes, projectId, IID or “no MR”, risk, `## Decisions`). Empty field = `MISSING`. Update `.dev/STATE.md` (`flow: feature`).

## Close

Manual: the last line of the chat message is `Next skill: \`dev-specify\``. Agent mode does not emit this line.
