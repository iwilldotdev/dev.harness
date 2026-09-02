---
name: dev-ship
description: >-
  Ships a verified feature or bug via a narrow MCP write allowlist after Gate S:
  preflight target/merge-base/diff, create GitLab MR, optional Jira comment or
  transition. Never accepts the MR, never force-pushes, never deploys. Use only
  after validation.md PASS and reviews without blockers. Draft MR only if
  INCOMPLETE and the user explicitly asks.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Ship

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md) and [references/preflight.md](references/preflight.md). The only skill with MCP writes — and only **after** Gate S.

## Preconditions

- **Feature:** `.dev/features/<slug>/validation.md` with PASS; reviews without BLOCK.
- **Bug:** reproduction + `.dev/bugs/<slug>/validation.md` with PASS; reviews without BLOCK.
- INCOMPLETE is **not** ready. Draft MR only if GitLab supports it **and** the user asks, with risks in the body.

```bash
python3 "$(dirname "$SKILL_DIR")/dev-shared/scripts/validate_state.py" .dev/STATE.md
```

Non-zero exit blocks.

## Preflight (before the gate)

Recalculate target, merge-base, `git status`, diff range, commits, potential conflicts. Rebase/branch update needs consent; never destructive (`reset --hard`, force-push, stash).

## ⛔ Gate S

Chat: diff range, commits, target branch, Jira, MR title/body, **exact** remote actions, risk. High-risk stays marked on the MR; confirm the right human reviewer was requested. The harness does **not** auto-approve or auto-merge.

Question prompt verbatim: `Gate S — Confirm remote actions`.

Approval authorizes **only** the listed actions.

## Allowlist after Gate S

- Always allowed if selected: `gitlab_save_merge_request` (create MR).
- Only if the gate marks them: `jira_add_comment`, `jira_transition_issue`, `jira_create_remote_issue_link`.
- **Never:** `gitlab_accept_merge_request`, `gitlab_add_commit`, force-push, deploy, production change by inference.

Afterwards: read the pipeline (`gitlab_get_pipeline` / jobs) and report status. Green CI does **not** prove a requirement or a fix.

`postmortem.md` only for a relevant incident **confirmed by the user**. Do not impose incident ceremony on an ordinary bug.

On a public repo: review internal links and excerpts in intake/ship before committing.
