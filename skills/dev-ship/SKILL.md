---
name: dev-ship
description: >-
  Ships a verified feature or bug after Gate S: push, create or update the
  GitLab MR, post the epic ship comment, and move the ticket to Code Review.
  Never accepts the MR, never force-pushes, never deploys. Use only after
  validation.md PASS and both reviews at APPROVE with no open Completeness
  row. Draft MR only if GitLab supports it and the user explicitly asks.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Ship

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md) and [references/preflight.md](references/preflight.md). The only skill with MCP writes — and only **after** Gate S.

## Preconditions

This section is the single definition of **ship-ready**. Cycles, agents, reviews, and `dev-fix-reviews` point here.

- **Feature:** `.dev/features/<slug>/validation.md` with PASS; both reviews ready (below).
- **Bug:** reproduction + `.dev/bugs/<slug>/validation.md` with PASS; both reviews ready (below).
- **Reviews ready:** the [readiness receipt](../dev-shared/references/evidence-contract.md#readiness-receipt) has each verdict `APPROVE`, both `open rows: 0` (an open row is a Completeness status of `gap` or `not-checked`), no file outside `.dev/` changed since either reviewed commit, including untracked files, and — when the flow cites a screen — calculated visual evidence whose Git SHA and Figma revision still match. A missing receipt or pair means the review ran outside the flow or in another conversation: stop before Gate S and re-run it. Do not reconstruct a report from memory. `ADJUST`, `BLOCK`, `INCOMPLETE`, an open row, a stale commit, or incomplete Figma coverage routes to `dev-fix-reviews` or the review.
- **Epic:** when `.dev/epic.json` exists, `validate_epic.py` must also exit 0. Any child verdict of `FAIL`, `INCOMPLETE`, or `BLOCK`, any open Completeness row, or any missing visual proof blocks the epic and names that child.
- INCOMPLETE is **not** ready. Draft MR only if GitLab supports it **and** the user asks, with risks in the body.

```bash
SHARED="$(dirname "$SKILL_DIR")/dev-shared/scripts"
python3 "$SHARED/validate_state.py" .dev/STATE.md
python3 "$(dirname "$SKILL_DIR")/dev-verify-feature/scripts/validate_feature.py" .dev/features/<slug>/validation.md --require-pass  # feature
python3 "$(dirname "$SKILL_DIR")/dev-verify-bug/scripts/validate_bug.py" .dev/bugs/<slug> --require-pass  # bug
python3 "$SHARED/validate_readiness.py" .dev/<features|bugs>/<slug>
python3 "$SHARED/validate_epic.py" .dev/epic.json --repo .  # only when the epic manifest exists
```

Any non-zero exit blocks.

## Preflight (before the gate)

Recalculate target, merge-base, `git status`, diff range, commits, potential conflicts. Rebase/branch update needs consent; never destructive (`reset --hard`, force-push, stash).

## ⛔ Gate S

Write the Gate briefing in chat before the question (confirming, artifact path of `validation.md`, summary of diff range, commits, target branch, Jira, MR title/body, and the exact remote actions, confirm vs reject). Prompt verbatim `Gate S — Confirm remote actions`.

Approval authorizes **only** the listed actions. High-risk stays marked on the MR; confirm the right human reviewer was requested. The harness does **not** auto-approve or auto-merge.

The briefing lists four remote actions when the ticket belongs to an epic that has `jira-ship-comment.md`: a normal push of the commits already made, create or update the MR, the Jira comment from that file, and the transition to **Code Review**. For [DEV-8943](https://construcode.atlassian.net/browse/DEV-8943) the file is `.dev/features/dev-8943-gravacao-anotacoes/jira-ship-comment.md`, next to `roadmap.md`. Do not invent the comment. Do not transition a ticket that is not in the MR. The transition id is read for that issue. It is not a fixed number from another ticket.

Agent orchestrators stop before this skill and do not load it. When the user then runs `dev-ship`, this gate stays manual even if `mode: agent`.

## Close

The last line of the chat message after the step finishes is `Next skill: none`.

## Allowlist after Gate S

- Always allowed if selected: a normal `git push` of the commits already made, and `gitlab_save_merge_request` (create or update the MR).
- When the epic has `jira-ship-comment.md` and the gate lists them: `jira_add_comment` from that template, then `jira_transition_issue` to Code Review.
- Only if the gate marks it: `jira_create_remote_issue_link`.
- **Never:** `gitlab_accept_merge_request`, `gitlab_add_commit`, force-push, deploy, production change by inference.

Afterwards: read the pipeline (`gitlab_get_pipeline` / jobs) and report status. Green CI does **not** prove a requirement or a fix.

`postmortem.md` only for a relevant incident **confirmed by the user**. Do not impose incident ceremony on an ordinary bug.

On a public repo: review internal links and excerpts in intake/ship before committing.
