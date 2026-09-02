---
name: dev-qa-guided-review
description: >-
  Second-layer QA review that crosses Jira acceptance criteria, Figma
  pixel-perfect design fidelity, and GitLab integration risks using only
  the `dev.mcp` server. Works on a merge request or, if none exists, the
  active branch (or branches the user names when more than one project is
  involved). Complements dev-mr-guided-review; does not replace code/nit review.
  Checkpoint gates: bind MCP, confirm target, extract context, resolve Figma
  screen pointers, cross-analyze, report. Use when the user asks for
  qa-guided-review, dev-qa-guided-review, QA review, ticket vs Figma,
  design fidelity, pixel-perfect, MR integration risks, or a QA pass against
  the Jira ticket and Figma frame.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# QA Guided Review

Second QA layer over a **GitLab MR** or, if the feature has no MR, the **active branch** (and other branches/projects only if the user names them). Crosses three dimensions with evidence or declares the dimension insufficient. Complements `dev-mr-guided-review`; does **not** redo nits, correctness, or architecture. Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md) at Step 0.

Report in English, chat-only. Read-only. Never write `QA_REVIEW.md` into the repo.

```
Step 0 Bind MCP → Gate A Target → Step 1 Extract → Step 1.5 Figma pointers
  → Gate B Context → Step 2 Cross-analysis → Gate C Findings → Step 3 Report
```

Each gate **stops**. Gate body (targets, nodes, URLs, hyperlinks) **always in chat**, so links stay clickable. The question prompt is only the short placeholder below. Without a structured question tool: inventory already in chat; then numbered labels only. Do not advance because it “looks sufficient”. When unsure, the user points — never choose alone.

## Load this skill

`SKILL_DIR` = the folder that contains this `SKILL.md`. Resolve at runtime; never hardcode the path or the product cwd.

- Step 0: read [references/mcp-allowlist.md](references/mcp-allowlist.md) in full.
- Step 1.5 and track (b): read [references/design-fidelity.md](references/design-fidelity.md) in full.
- Step 2: read [references/integration-heuristics.md](references/integration-heuristics.md) in full.
- Step 3: follow [references/report-template.md](references/report-template.md) exactly.
- Parser: `python3 "$SKILL_DIR/scripts/extract_refs.py"` (no network). If missing, stop.

## Hard rules

1. **`dev.mcp` only.** Discover a ready server named `dev.mcp` (hosts may prefix the name). If it is not ready, stop. Official Figma / Atlassian / GitLab MCP servers are forbidden.
2. **Read-only.** Denylist in `mcp-allowlist.md`. Comment drafts stay in chat.
3. **Evidence-or-zero.** Without `path:line`, a Jira field, or a Figma **screen** node, the finding does not enter. Do not complete a missing AC. Do not treat a green pipeline as AC coverage.
4. **Zero hardcoded target.** No `projectId`, IID, path, or file key in this skill.
5. **Does not replace `dev-mr-guided-review`.** One report line points to it.
6. **Outside MCP:** `Read` / `Grep` / `Glob`; `git remote`, `git branch`, `git merge-base`, `git diff <base>...<head>`. Do not use `glab` as the primary path.
7. **Figma quota.** Prefer `figma_get_design_context` with `nodeIds`. Never `figma_get_file` without `depth`/`ids`.
8. **Pixel-perfect on (b).** A spec-sheet does not replace a screen. Do not claim (b) OK without a screenshot of a **screen** frame. Do not close a visual GAP with invented UI (generic Modal, copy from another i18n key, “equivalent flow”). Detail in `design-fidelity.md`.
9. **When unsure, ask.** Several MRs, 0 MR, several remotes/repos, spec vs screen frame, degrading a dimension: stop and ask. Do not invent the target.

## Gates — chat then ask

At **every** checkpoint:

1. Write the body in **chat** (Markdown). Include clickable URLs (MR, Jira, Figma with `node-id`, screenshots). Spec vs screen nodes, `projectId`, IID, branch, merge-base, criteria, and mismatches stay **here**.
2. Then ask. If the host has a structured question tool, use it (`allow_multiple: false`). The `prompt` is **only** the gate placeholder — one line, no IDs, no URLs, no node list. Labels are the short phrases below.
3. **Do not** copy inventory, hyperlinks, `fileKey`, `node-id`, or Jira keys into the prompt or labels.

Placeholders (verbatim):

| Gate | `id` | `prompt` |
|---|---|---|
| A | `gate-a-target` | `Gate A — Confirm target` |
| A (ambiguous base) | `gate-a-base` | `Gate A — Confirm merge-base` |
| B | `gate-b-context` | `Gate B — Enough context?` |
| C | `gate-c-findings` | `Gate C — Confirm findings?` |

**Gate A — options** (build from Step 0; never fictional options; candidate details already in chat):

- 1 MR: `confirm-mr` “Confirm this MR”; `use-branch` “Review the active branch (no MR)”; `multi-project` “There is another project/branch — I will point to it”.
- 0 MR: `use-branch` “Review the active branch vs merge-base”; `paste-mr` “I will paste an MR URL/IID”; `multi-project` “There is another project/branch — I will point to it”.
- >1 MR: one option per IID (`mr-<iid>`, label `MR !<iid>` — no URL) + `use-branch` + `multi-project`.
- Several projects: one option per short detected name + `multi-project`.
- Ambiguous base (`gate-a-base`): one option per short ref (`origin/main`, `upstream`, …). SHA and command stay in chat.

Do not advance to Step 1 until the answer.

**Gate B — options** (omit those that do not apply; spec vs screen inventory only in chat):

- `proceed` “Enough context; continue to analysis”
- `na-a` “Authorize (a) N/A”
- `na-b` “Authorize (b) N/A (no UI / no Figma)”
- `integration-only` “Dimension (c) only; (a) and (b) N/A”
- `fix-frames` “Fix screen frames”
- `stop` “Stop”

Do not start Step 2 if (a) and (b) are missing, unless `integration-only`. A missing dimension degrades only with `na-a` / `na-b`. Inventory with only a spec-sheet (no screen) is **not** enough for (b): `fix-frames` or (b) incomplete — do not treat spec as screen.

**Gate C — options** (findings draft only in chat):

- `confirm-report` “Confirm findings and emit the report”
- `wrong-screen` “Fix the screen frame”
- `false-positive` “There is a false positive / poorly extracted AC”
- `block-b-ok` “Do not confirm screens; (b) cannot be OK”

Without confirmation of **screen** `node-id`s (in chat + option), it is forbidden to emit a canonical report with (b) OK.

## STEP 0 — Bind MCP and target

1. Discover a ready `dev.mcp` server (hosts may prefix the name).
2. Host auth handshake only if required; re-check ready.
3. Smoke: `gitlab_whoami`. `figma_whoami` if (b) will be attempted.
4. Candidate the target **without** bulk Jira/Figma extract:

**Target order**

1. User text → `extract_refs.py`. `gitlab.mrs[]` if there is a URL/`group/project!iid`.
2. Local git (each involved repo if the user already named more than one; otherwise only the current workspace):
   - `git remote get-url origin` (and `gitlab` if present) → `extract_refs.py` → `projectId`.
   - `git branch --show-current` → `sourceBranch`.
   - `git rev-parse --show-toplevel` only for Read/Grep; never as a GitLab ID.
   - Extra remotes / sibling folders: **do not** assume a second project. Gate A `multi-project`.
3. MCP: with `projectId` + branch and no IID → `gitlab_list_merge_requests` (`state: opened`, `sourceBranch`).
   - 0 / >1 / 1 → Gate A as above.
4. Unreadable remote → `gitlab_list_projects` (`membership: true`, `search` by folder name). Never pick the first list item without Gate A.

**Branch mode (0 MR or user chooses `use-branch`):** base = `@{upstream}` if it exists; else `origin/HEAD`; else `origin/main` | `origin/master` | `origin/develop`. `git merge-base HEAD <base>`. If the base is ambiguous: list refs/SHA **in chat**, then ask `gate-a-base`. Diff = `git diff <merge-base>...<sourceBranch>`. Do not invent an IID.

Do not call `gitlab_get_merge_request` with diffs before Gate A.

**⛔ Gate A** — body in chat (server name, `projectId`, IID or “no MR”, branch, merge-base, title, links). Then ask with prompt verbatim `Gate A — Confirm target`.

## STEP 1 — Extract context

With the target confirmed:

1. **MR mode:** `gitlab_get_merge_request` (`includeDiffs`, `includeCommits`, `includeNotes`, `includePipelines`). Truncated diff → `git diff <target>...<source>`.
2. **Branch mode:** `git diff <merge-base>...<HEAD>` (and `--stat`). `gitlab_list_pipelines` (`ref` = branch) if `projectId` is known; failed jobs → `gitlab_get_pipeline` + `gitlab_get_pipeline_jobs`. Without an IID, do not call `gitlab_get_merge_request`.
3. Concatenate title/description/notes (MR) **or** branch + `git log <merge-base>..HEAD --oneline` + user text → `extract_refs.py`.
4. **Jira:** `jira_get_issue` + `jira_get_remote_issue_links`. `jira_search_jql` only if the key is ambiguous. Run `extract_refs.py` on description + links.
5. **Figma (ticket nodes):** for each URL/`fileKey`+`node-id`, `figma_get_design_context` + `figma_get_metadata` (required; not “if needed”). Then Step 1.5. `figma_download_assets` only if the AC cites an asset. Never the whole file.
6. **CI (MR mode):** failed pipelines in the payload → jobs. Cap = status/name (no log).
7. **Contracts:** `gitlab_get_repository_file` only for OpenAPI/types/clients cited in the diff. `gitlab_search` `scope: blobs` only on rename/move. `gitlab_get_commit` only for a specific SHA. Branch mode: `ref` = `sourceBranch`.
8. **Confluence:** only if a link points to a page **and** Jira has no AC/Figma. Announce at Gate B.

## STEP 1.5 — Screen pointers (required if Figma is present)

Follow [references/design-fidelity.md](references/design-fidelity.md). Gate B inventory must separate **spec** and **screen**. One hop of “see this screen” + siblings in the section. Unresolved pointer → (b) incomplete.

**⛔ Gate B** — checklist in chat (diffs; Jira; spec vs screen with Figma URLs; Confluence). Then ask with prompt verbatim `Gate B — Enough context?`.

## STEP 2 — Cross-analysis

Read `integration-heuristics.md` and `design-fidelity.md` again for (b). No new tools except a punctual allowlist hole.

**(a) Business rules.** Jira criteria × diff/test (`path:line`) or `MISSING`.

**(b) Pixel-perfect.** Only frames classified `screen`. Minimum method per surface: screen screenshot + code (Tailwind/tokens/copy/states). Mismatch: layout, typography, overlay, asset, spacing, token, state, copy, missing. “Looks like the DS” ≠ OK. Without a confirmed screen, do not mark OK.

**(c) Integration.** Contracts, breaking changes, callers outside the diff, failed CI, flags. Failure scenario + blast radius.

**⛔ Gate C** — draft in chat (criteria, mismatches with **screen** frame links, risks, unknowns). Then ask with prompt verbatim `Gate C — Confirm findings?`. Without `confirm-report` + confirmed screens, (b) is not OK in the report.

## STEP 3 — Report

Fill `report-template.md` in chat. No write tool. Section 9 only if requested. Verdict: `APPROVE` / `ADJUST` / `BLOCK` / `INCOMPLETE`.

Branch mode: section 1 says **MR: none (branch review)** + merge-base; do not invent an IID.

## After the report

This skill does not implement. If the user asks to fix GAPs:

- GAP (b): open the **screen** `node-id` (`figma_get_design_context` + screenshot) **before** any UI. Forbidden: generic Modal/Drawer, copy from another i18n key, “equivalent” flow.
- Marketing/onboarding frame: that layout, or ask product.
- GAP (a)/(c): evidence already cited; no extra refactor.
- Still forbidden to post to MR/Jira.

## Examples

**Example 1.** “run qa-guided-review on this MR” → Step 0 → Gate A → 1 → 1.5 → Gate B → 2 → Gate C → report.

**Example 2.** URL `.../merge_requests/42` → parser → Gate A confirms.

**Example 3.** Feature on a branch, 0 MR → Gate A `use-branch` (recommended default) → diff vs merge-base.

**Example 4.** Ticket with Figma `85:1999` (“SEE THIS SCREEN”) → 1.5 resolves screen/modal. Gate B lists spec **and** screen. Gate C compares the screen screenshot. Forbidden: (b) OK or a fix via generic Modal.

**Example 5.** Two repos in the feature → Gate A `multi-project`; the user names the branches. Do not review the second repo alone.

**Example 6 (wrong skill).** Nits/architecture → `dev-mr-guided-review`.

## Troubleshooting

**Missing server.** Connect the `dev.mcp` MCP server; complete host auth if required. No other MCP.

**`gitlab_whoami` fails.** Host auth; stop if it persists.

**0 MR.** Branch mode via Gate A; do not invent an IID.

**Several MRs / several projects.** Gate A; never choose alone.

**Inventory is only a spec-sheet.** Step 1.5 incomplete. Do not degrade (b) to the spec.

**Figma variables 403.** Unknown; (b) not OK.

**Figma 429.** Only context+screenshot of nodes already in the inventory.

**Truncated diff / no MR.** Local `git diff <base>...<head>`.

**No structured question tool.** Inventory is already in chat; then numbered labels only. Do not dump nodes/URLs again into the options.

**Long question text.** Wrong: inventory in the prompt. Correct: body in chat, placeholder verbatim.

**Missing script.** `$SKILL_DIR/scripts/extract_refs.py` must exist.
