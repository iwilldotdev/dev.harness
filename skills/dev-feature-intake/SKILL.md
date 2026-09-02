---
name: dev-feature-intake
description: >-
  Feature intake via dev.mcp: bind server, resolve GitLab target, extract Jira
  and Figma (spec vs screen), classify complexity and risk, and write
  .dev/features/<slug>/intake.md. Use at the start of a feature. Stops at Gate
  F-A. Read-only. Do not use for bugs (use dev-bug-intake).
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Feature intake

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). MCP read-only. Do not invent ACs.

```
Step 0 Bind → target (parser + git + MR) → Gate A if ambiguous → Jira/Figma/CI
  → code grounding → risk/complexity → Gate F-A → intake.md
```

## Steps

1. Bind `dev.mcp`. Smoke `gitlab_whoami`. `figma_whoami` if a Figma URL is present.
2. User text → `extract_refs.py`. Remote `origin` → `projectId`. Current branch. No IID: `gitlab_list_merge_requests` (`state: opened`, `sourceBranch`). 0/>1/several projects → Gate A (`Gate A — Confirm target`). Do not invent an IID. Branch mode: merge-base; ambiguous base → `Gate A — Confirm merge-base`.
3. After target: `jira_get_issue` + `jira_get_remote_issue_links`. Figma: `figma_get_design_context` + `figma_get_metadata` on each node. Step 1.5: read [../dev-qa-guided-review/references/design-fidelity.md](../dev-qa-guided-review/references/design-fidelity.md) — spec-sheet ≠ screen. Confluence only if linked and Jira has no AC/Figma.
4. Read-only grounding: patterns, contracts, tests, docs. Verification surface (unit/API/browser/state). Do **not** propose architecture yet.
5. Classify complexity (small/medium/large) and risk (normal/high) with evidence. Skip design/tasks only if small **and** normal — propose at Gate F-A, do not decide alone.

**⛔ Gate F-A** — chat: target, Jira, spec vs screen (URLs), MR/branch, risk, proposed skip. Prompt verbatim `Gate F-A — Confirm context`.

Artifact: `.dev/features/<slug>/intake.md` (keys, fileKey, spec **and** screen node-id, projectId, IID or “no MR”, risk). Empty field = `MISSING`. Update `.dev/STATE.md` (`flow: feature`).
