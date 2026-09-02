---
name: dev-mr-guided-review
description: >-
  Two-phase GitLab MR walkthrough via dev.mcp: understand goal and a concrete
  example first, then thorough code review of correctness, regressions, coverage
  and architecture fit — not nits. Read-only; never posts to the MR. Use when
  reviewing, understanding, or walking through an MR or branch change. Complements
  dev-qa-guided-review. High-risk diffs flag human specialist review without
  claiming security approval.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# MR Guided Review

Review companion. **Understand first, critique second.** Does not post to the MR. Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). Allowlist: read-only.

## Hard rules

- **Never post** to the MR (comment, approval, `gitlab_save_merge_request`, `gitlab_create_merge_request_note`, `gitlab_accept_merge_request`, `gitlab_add_commit`). Drafts stay in chat.
- Concise. No style nits unless they are a real bug. Each issue: `file:line` — what, why, failure scenario.
- Evidence-or-zero. A green pipeline does not prove an AC.
- High-risk (auth, data, migration, finance, concurrency, contract): flag specialist human review. Do **not** fabricate “security approved”.

## `dev.mcp` adapter

Default: MCP, not `glab`.

1. Resolve `projectId` + IID (URL, remote+branch, or user) via `extract_refs.py`. No IID: branch mode (`git merge-base`); do not invent an IID.
2. Smoke `gitlab_whoami`. Gate A if the target is ambiguous (same contract as QA).
3. `gitlab_get_merge_request` (`includeDiffs`, `includeCommits`, `includeNotes`). Truncated diff → `git diff <target>...<source>`.
4. Jira keys in title/description/branch: `jira_get_issue` (read).

## Phase 1 — Understand

- **Problem** (1–2 sentences)
- **Change** (1–2 sentences)
- **How it works** (what is needed)
- **Simple example** — required (input→output, visible scenario, or a minimal walkthrough)
- **Scope** — areas, not a file list

**Stop.** Question prompt verbatim: `Ready to review the code changes thoroughly?` Labels: `yes` “Yes, review the code”; `stay` “Stay in Phase 1”. Do not advance without yes.

## Phase 2 — Review

Only after confirmation. If `gitlab-coding-principles` or `.ai/code-review.md` exists, apply it.

Order: correctness → regressions/security → coverage → architecture fit. No nits. Short verdict: blockers or approve.

Close by pointing to `dev-qa-guided-review` for AC × Figma × integration.
