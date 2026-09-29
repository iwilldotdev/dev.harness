# MCP allowlist — `dev.mcp`

The only source of business tools for this skill. Read this at Step 0.

## Runtime bind

1. Discover a ready MCP server named `dev.mcp`. Hosts may prefix the name (for example `user-dev.mcp`). Do not use another server just because the name contains `mcp`.
2. Require a ready/connected status. If the host reports auth-needed, error, or loading, do not treat it as usable.
3. Invoke tools by their short names below (no server-name prefix).
4. If bind fails: **stop**. Do not use the official Figma, Atlassian/Rovo, or GitLab MCP servers, or any other wrapper with different schemas.
5. Host auth is the only host-side tool allowed, and only when bind indicates authentication is required.

Do not hardcode a GitLab host, projectId, Figma file key, or Jira key in this file.

## Absolute denylist (never call)

Writes / mutations. Text drafts stay in chat.

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

## Read allowlist

Only these business tools (plus host auth). If a server tool is not on this list, do not call it.

### Host

- Host auth — only if the server requires authentication.

Structured question tools (gates A/B/C) are **not** `dev.mcp` tools. Use them when the host provides one. `prompt` = the skill’s short placeholder; inventory and hyperlinks stay in chat.

### GitLab (target, diff, CI, contracts)

- `gitlab_whoami`
- `gitlab_list_projects` — `projectId` fallback when the remote does not parse; never pick the first list item without Gate A.
- `gitlab_list_merge_requests`
- `gitlab_get_merge_request` — MR mode, after Gate A; `includeDiffs`, `includeCommits`, `includeNotes`, `includePipelines`. Without an IID (branch mode), do not call.
- `gitlab_get_issue` — if the MR cites a GitLab issue, not Jira.
- `gitlab_get_commit`
- `gitlab_get_repository_file` — neighboring contracts cited in the diff; `content` is base64.
- `gitlab_list_pipelines` — MR mode via payload; branch mode with `ref` = active branch.
- `gitlab_get_pipeline`
- `gitlab_get_pipeline_jobs` — CI evidence cap: status/name. No log tool.
- `gitlab_get_job`
- `gitlab_search` — only `scope: blobs` (or `commits`) when rename/move hides the contract. No broad search.
- `gitlab_search_labels` — only if an AC cites a label.
- `gitlab_list_project_members` — only if an AC cites roles; not for “who approved”.
- `gitlab_list_wiki_pages` — only if the ticket points at GitLab wiki and Jira/Figma are missing.

### Jira (business rules)

- `jira_get_issue`
- `jira_get_remote_issue_links`
- `jira_search_jql` — ambiguous key only (`key = X OR parent = X`), not a project sweep.
- `jira_get_projects` — only if the ticket key is ambiguous.
- `jira_get_issue_types_metadata` — only if an acceptance field must be named.
- `jira_get_transitions` — only if the AC cites workflow state; not to transition.
- `jira_get_issue_link_types` — only to interpret issuelinks already read.
- `jira_lookup_account_id` — only if an AC cites a person and the field is an opaque accountId.

### Figma (design fidelity)

- `figma_whoami` — smoke for dimension (b).
- `figma_get_design_context` — preferred (`nodeIds`, `includeScreenshot: true`, `includeVariables: true`). Required on the ticket node **and** each screen hop (Step 1.5).
- `figma_get_screenshot` — dimension (b) evidence is the **screen/component** screenshot, not the spec-sheet.
- `figma_get_metadata` — required at Step 1.5 (pointers, hyperlinks, section siblings).
- `figma_get_variable_defs`
- `figma_get_comments`
- `figma_download_assets` — only if the AC cites an icon/asset.
- `figma_get_file` — last resort, always with `depth` and/or `ids`. Never the whole root document.

### Confluence (optional enrichment — not a review dimension)

Use only after announcing at Gate B, and only if a remote link/URL points to a page **and** Jira has neither AC nor Figma.

- `confluence_get_page`
- `confluence_get_page_descendants`
- `confluence_get_pages_in_space`
- `confluence_get_spaces`
- `confluence_search_cql` — only to find the already cited page, not exploration.
- `confluence_get_page_footer_comments`
- `confluence_get_page_inline_comments`

## Outside MCP (allowed)

- `Read`, `Grep`, `Glob` in the workspace working tree.
- Git: `remote get-url`, `branch --show-current`, `rev-parse --show-toplevel`, `rev-parse --abbrev-ref @{upstream}`, `symbolic-ref refs/remotes/origin/HEAD`, `merge-base`, `diff <base>...<head>`, `log <base>..HEAD --oneline`.
- Host: a structured question tool at every Gate A/B/C when it exists (not a `dev.mcp` tool). Manual mode only; in `mode: agent`, follow the agent-mode policy instead of asking.
- `python3 "$SKILL_DIR/scripts/extract_refs.py"`.

Forbidden: `glab` as the primary path; any MCP that is not `dev.mcp` / a host-prefixed `dev.mcp`.
