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

Review companion. **Understand first, critique second.** Does not post to the MR. Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). MCP allowlist: read-only. The only file this skill writes is the readiness receipt, and only inside an active flow.

## Hard rules

- **Never post** to the MR (comment, approval, `gitlab_save_merge_request`, `gitlab_create_merge_request_note`, `gitlab_accept_merge_request`, `gitlab_add_commit`). Drafts stay in chat.
- Concise. No style nits unless they are a real bug. Each issue: `file:line` — what, why, failure scenario.
- Evidence-or-zero. A green pipeline does not prove an AC.
- High-risk (auth, data, migration, finance, concurrency, contract): flag specialist human review. Do **not** fabricate “security approved”.

## `dev.mcp` adapter

Default: MCP, not `glab`.

1. Resolve `projectId` + IID (URL, remote+branch, or user) via `extract_refs.py`. No IID: branch mode (`git merge-base`); do not invent an IID.
2. Smoke `gitlab_whoami`. Gate A if the target is ambiguous (same contract as QA). Write the Gate briefing in chat before the question. If `.dev/STATE.md` has `mode: agent`, do not ask: follow [../dev-shared/references/agent-mode.md](../dev-shared/references/agent-mode.md).
3. `gitlab_get_merge_request` (`includeDiffs`, `includeCommits`, `includeNotes`). Truncated diff → `git diff <target>...<source>`.
4. Jira keys in title/description/branch: `jira_get_issue` (read).

## Phase 1 — Understand

- **Problem** (1–2 sentences)
- **Change** (1–2 sentences)
- **How it works** (what is needed)
- **Simple example** — required (input→output, visible scenario, or a minimal walkthrough)
- **Scope** — areas, not a file list

**Stop.** Write the Gate briefing in chat before the question (confirming, artifact `none` unless a note file exists, summary of problem/change/example, confirm vs stay). Question prompt verbatim: `Ready to review the code changes thoroughly?` Labels: `yes` “Yes, review the code”; `stay` “Stay in Phase 1”. Do not advance without yes. In `mode: agent`, record `decision: proceed` and continue to Phase 2 without asking.

## Phase 2 — Review

Manual mode starts only after `yes`. Agent mode starts after `decision: proceed`. If `gitlab-coding-principles` or `.ai/code-review.md` exists, apply it.

Order: correctness → regressions/security → coverage → architecture fit. No nits. The first line of the verdict is exactly `APPROVE`, `ADJUST`, `BLOCK`, or `INCOMPLETE`.

## Completeness

Close Phase 2 with this profile of the change. One row per correctness, regression, and coverage item:

| Item | Status | Evidence | Correction |
| --- | --- | --- | --- |
| finding or checked area | done / gap / not-checked | `path:line` | `dev-execute` / `dev-fix-bug` / `dev-debug` / none |

`gap` is a defect that must be corrected. `not-checked` is in scope and was not reviewed. Do not bury a blocker in the verdict sentence only. Verdict is `APPROVE` only when no row is `gap` or `not-checked`; otherwise `ADJUST`, `BLOCK`, or `INCOMPLETE`.

Close by pointing to `dev-qa-guided-review` for AC × Figma × integration.

The full report stays in chat. Inside an active flow, rewrite the three `MR` lines of the readiness receipt after every run, whatever the verdict, as defined in [../dev-shared/references/evidence-contract.md](../dev-shared/references/evidence-contract.md#readiness-receipt). Outside a flow, write nothing.

## Close

Manual: the last line of the chat message is `Next skill: \`dev-mr-guided-review\`` when the verdict is `INCOMPLETE` because the target, the diff, or access is missing, so the same review runs again once that is available. `Next skill: \`dev-qa-guided-review\`` when the verdict is `APPROVE`, `ADJUST`, or `BLOCK`, so the second review still runs. Agent mode does not emit this line.
