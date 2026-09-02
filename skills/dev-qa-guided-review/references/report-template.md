# QA Guided Review report template

Fill in chat, in English. Do not write it into the repo. Do not invent sections. Omit section 9 unless the user asks for a paste draft.

Tone: concise, ranked, no style nits (those belong to `dev-mr-guided-review`).

`(b) OK` requires: each UI surface in the diff compared to a **screen** frame (not a spec-sheet), a screenshot of that node cited, and confirmation of those `node-id`s at Gate C. Without that: `GAP`, `INCOMPLETE`, or authorized `N/A` — never OK.

```markdown
# QA Guided Review

## 1. Target

- **Project:** `<projectId>` (repeat if the user confirmed more than one)
- **Mode:** MR | branch
- **MR:** `!<iid>` — `<url>`  |  `none (branch review)`
- **Title:** … | n/a in branch mode
- **Branches:** `<source>` → `<target or merge-base>`
- **Merge-base (branch mode):** `<short sha>` on `<origin/main|upstream|…>`
- **Author:** … | n/a
- **State:** opened | merged | closed | locked | n/a (branch)
- **Jira:** `PROJ-123` | N/A (authorized)
- **Figma spec:** `fileKey` / `node-id` / name
- **Figma screen:** `fileKey` / `node-id` / name  |  unresolved

## 2. QA verdict

`APPROVE` | `ADJUST` | `BLOCK` | `INCOMPLETE`

One sentence: what blocks merge (or the future branch merge), or why it is incomplete.

## 3. Dimension coverage

| Dimension | Status | Reason |
|---|---|---|
| (a) Business rules | OK / GAP / N/A | … |
| (b) Design fidelity | OK / GAP / N/A / INCOMPLETE | … |
| (c) Integration risks | OK / GAP / N/A | … |

`N/A` only with Gate B authorization (`na-a` / `na-b` / `integration-only`), or if the surface does not exist (diff with no UI → (b) N/A). Spec-sheet without a resolved screen → (b) `INCOMPLETE`, not silent N/A.

## 4. (a) Business rules

One row per criterion extracted from Jira. No extractable criterion and no authorized N/A → do not write “looks fine”; verdict `INCOMPLETE`.

| Criterion (Jira field quote) | Evidence | Result |
|---|---|---|
| “…” — `PROJ-123` description / AC | `path/to/file.ts:12` or `MISSING` | OK / GAP |

## 5. (b) Design fidelity (pixel-perfect)

Required at the top of this section:

- **Spec frame:** `fileKey` / `<id>` / name — feeds states; does **not** replace (b)
- **Screen/component frame:** `fileKey` / `<id>` / name
- **Screen/component screenshot:** `<url>` (not the spec-sheet)
- **States covered:** default / hover / open / empty / disabled (those the spec cites)

One row per visible surface in the diff. Line `OK` only with a **screen** screenshot + component `path:line`.

| Surface / state | Screen frame | Frame requirement | What the diff does | Mismatch type | Evidence |
|---|---|---|---|---|---|
| … | `203:13054` | … | … | layout / typography / overlay / asset / spacing / token / state / copy / missing | screen screenshot + `path:line` |

Types: `layout` (position, size, radius) · `typography` (project custom scale, not a generic DS) · `overlay` · `asset` · `spacing` · `token` · `state` · `copy` · `missing`.

Forbidden: mark the section OK because a generic `Modal`/`Drawer` exists, copy from another i18n key, or an “equivalent flow”.

No screen frame: `INCOMPLETE — “see this screen” pointer unresolved` (or `N/A` only if Gate B `na-b`).

## 6. (c) Integration risks

Most serious first. Each item:

- **`path:line` — title**
  - Failure scenario: …
  - Blast radius: callers / contract / CI job `name (status)`
  - No evidence → do not list.

If there is no evidenced risk: `No evidenced integration risk in this diff.`

## 7. Out of scope for this skill

Implementation correctness, nits, naming, formatting, and general architecture fit → `dev-mr-guided-review`. Do not duplicate.

Implementing a (b) GAP without opening the **screen** frame is a product blocker; this skill does not write the code, but the report must say so.

## 8. Unknowns

What this run does not cover. Examples:

- CI job log (status/name only via `gitlab_get_pipeline_jobs`)
- Official Figma MCP proprietary codegen
- Figma variables 403 (`file_variables:read`) — (b) cannot be OK
- Cropped frame / 429 quota
- Acceptance criterion only in an unread attachment/image
- Unidentified Jira AC field
- Second feature repository not named by the user

## 9. Draft for a human to paste (optional)

Only if requested. MR note text. **Do not send** with `gitlab_create_merge_request_note`.
```
