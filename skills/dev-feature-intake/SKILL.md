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
2. User text → `extract_refs.py` (`jira_keys`, `figma`, `figma_pointers`, `gitlab`). Remote `origin` → `projectId`. Current branch. No IID: `gitlab_list_merge_requests` (`state: opened`, `sourceBranch`). Do not invent an IID. Branch mode: merge-base. When the ticket is an epic (or names one), pull its children with **one** `jira_search_jql` (`parent = <epic> ORDER BY rank`) instead of N `jira_get_issue` calls; then fetch each child with trimmed `fields`.
3. If the ticket is a child of DEV-8943, read `.dev/features/dev-8943-gravacao-anotacoes/roadmap.md` and `jira-ship-comment.md` before the gap round. The ship comment is part of every cycle of that epic.
4. After the target is readable: `jira_normalize_issue` (plus the raw issue only when a field is missing from it) and `jira_get_remote_issue_links` on each ticket. Figma: `figma_get_frames` first (one recursive call) to build the ticket × frame draft (`map_tickets_frames.py --frames <payload.json> --keys <keys> --strict`; name matches are drafts, and a versioned `--overrides` file records a human mapping). Then `figma_get_design_context` with a node id and `figma_fetch_screenshot` at scale 1 for each screen, state, and viewport. Save payload + verified PNG into the Figma pack, write `visual-manifest.json` (requirement × screen × state × viewport), and run `figma_pack.py --check` and `validate_intake.py`. An unresolved pointer, frame, criterion, state, or viewport blocks Gate F-A. Confluence only if linked and Jira has no AC/Figma.
5. Read-only grounding: patterns, contracts, tests, docs. Verification surface (unit/API/browser/state). Do **not** propose architecture yet.
6. Classify complexity (small/medium/large) and risk (normal/high) with evidence. Skip design/tasks only if small, normal risk, and no screen — propose that at Gate F-A, do not decide alone in manual mode. A screen, a large size, or high risk is not a skip.

## Gap round (once)

Before Gate F-A, list only facts the ticket, Figma, git, and code do not answer: ambiguous target (0 / many MRs, several projects, ambiguous base), missing AC, unresolved screen frame.

- No gap → do not ask.
- One or more gaps → one `gate-intake-gaps` form, as defined in [../dev-shared/references/gates.md](../dev-shared/references/gates.md#intake-gap-round). The briefing states what is already known; the form has one labeled question per gap.
- Record each answer in `intake.md` under `## Decisions`.
- Later steps read `## Decisions` and do not ask the same fact again.

In `mode: agent` this is the only question in the cycle. Gate F-A is then decided from those answers plus the evidence. Follow [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md).

**⛔ Gate F-A** — Write the Gate briefing in chat before the question (confirming, artifact path, summary of target, Jira, spec vs screen, risk, proposed skip, confirm vs reject). Prompt verbatim `Gate F-A — Confirm context`. An ambiguous target is resolved by the `Target MR` / `Merge-base` questions of the gap round, not by a separate Gate A round.

Artifact: `.dev/features/<slug>/intake.md` (keys, fileKey, spec **and** screen node-id, visual-contract notes, projectId, IID or “no MR”, risk, `## Decisions`). Empty field = `MISSING`. The Figma pack (`figma/`) belongs to the flow from this step on. Update `.dev/STATE.md` (`flow: feature`).

## Close

Manual: the last line of the chat message is `Next skill: \`dev-specify\``. Agent mode does not emit this line.
