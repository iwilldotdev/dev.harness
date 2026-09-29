# Allowlists per step

No-escalation: the current skill does **not** inherit the next skill’s write tools. The orchestrator ends the skill and loads the next one.

## Absolute denylist (never, except `dev-ship` after Gate S)

- `gitlab_save_merge_request`
- `gitlab_create_merge_request_note`
- `gitlab_accept_merge_request`
- `gitlab_add_branch`
- `gitlab_add_commit`
- `gitlab_create_issue`
- `jira_create_issue`
- `jira_edit_issue`
- `jira_transition_issue`
- `jira_add_comment`
- `jira_add_worklog`
- `jira_create_issue_link`
- `jira_create_remote_issue_link`
- `confluence_create_page`
- `confluence_update_page`
- `confluence_create_footer_comment`
- `confluence_create_inline_comment`

## Read-only MCP (intakes, planning, reproduce, debug, verify, reviews, routers)

All read tools in [dev-qa-guided-review/references/mcp-allowlist.md](../../dev-qa-guided-review/references/mcp-allowlist.md) plus host auth when required. `dev-debug` diagnoses; it does **not** patch.

Skills: `dev-cycle`, `dev-feature-cycle`, `dev-feature-agent`, `dev-bug-cycle`, `dev-bug-agent`, `dev-feature-intake`, `dev-bug-intake`, `dev-specify`, `dev-design`, `dev-tasks`, `dev-reproduce-bug`, `dev-debug`, `dev-verify-feature`, `dev-verify-bug`, `dev-mr-guided-review`, `dev-qa-guided-review`.

## Working tree (no MCP writes)

`dev-execute`, `dev-fix-bug`, `dev-fix-reviews`: Read/Grep/Glob, local git add/commit, tests. MCP stays read-only (CI, Figma screen, Jira AC).

`dev-mr-guided-review` and `dev-qa-guided-review` write one file: the [readiness receipt](evidence-contract.md#readiness-receipt), and only inside an active flow. Nothing else, no commit.

## `dev-ship` (after Gate S)

Narrow allowlist: `gitlab_save_merge_request`. Optional if the gate selects them: `jira_add_comment`, `jira_transition_issue`, `jira_create_remote_issue_link`. Never `gitlab_accept_merge_request`. Never force-push. Never remote `gitlab_add_commit`.

## Outside MCP

`Read`, `Grep`, `Glob`; git `remote`, `branch`, `merge-base`, `diff`, `log`, `show`, `status`. Python scripts with no network. Do not use `glab` as the primary path.

## Git safety

Capture branch/status/diff **before** writing. Preserve unrelated changes. Forbidden: `reset --hard`, destructive checkout, automatic stash, force-push. Isolate in a worktree/scratch — never `git stash`.
