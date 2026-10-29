# Changelog

This harness uses SemVer. Contract, gate, and artifact changes are recorded here.

## 0.3.0 — 2026-10-29

- Figma pack: intake/design persist each screen as `figma/<node-id>.json` + `.png` + `pack.json` (`lastModified`, `fetchedAt`); execute, verify, and reviews read the pack instead of refetching. New `dev-shared/scripts/figma_pack.py` builds the manifest and `--check` fails while a screen cited in `design.md` lacks its pack files.
- Ship-ready now includes Figma coverage: the readiness receipt gains `QA figma-screens: <comparadas>/<citadas>`; `validate_readiness.py` requires it when `design.md` has a `## Visual contract`, requires `comparadas ≥ citadas`, and requires a pack PNG for every cited screen.
- `validate_design.py` checks row content: every Visual contract row must cite the screen node-id and carry a concrete fact (measure, hex color, or literal copy). `validate_spec.py` fails a UI requirement section without a node-id and a Visual contract screen not cited by any requirement. `validate_tasks.py` fails a UI task without screen node-ids (explicit `UI: sem screen` waives it).
- Pointer resolution no longer depends on prose: `figma_pointers` in `extract_refs.py` reads `prototypeNodeId`/`destinationNodeId`/hyperlink destinations, and `figma_get_design_context` (dev.mcp ≥ with pointers) returns `hyperlink` and `reactions` per node; metadata XML carries `hyperlinkNode`/`prototypeNode` attrs.
- dev.mcp additions consumed by the flow: `figma_get_file_meta` (freshness), `figma_get_frames` (ticket × frame index), `fields` block selection, `truncation.nextChildIds`, and `lastModified` on the design-context payload.
- New operational scripts in `dev-shared/scripts`: `map_tickets_frames.py` (draft ticket × frame × repo mapping from a `figma_get_frames` payload), `legacy_check.py` (CRLF/BOM drift, duplicated `<Compile>`/`appSettings` for the Windows-only legacy repo), and `merge_wave.py` (ordered task-worktree merges with conflict abort and post-merge checks).
- Bug flows bind to the same fidelity contract: visual bug fixes cite the screen node-id from the pack; verify-bug names the compared screens.

## 0.2.0 — 2026-09-29

- Visual contract for Figma screens: fixed sizing, absolute position, and complex styles in specify, design, execute, and review.
- Gate briefing in chat before every question (artifact path and summary). One intake gap round; later gates do not re-ask those facts.
- Completeness profile on QA, MR review, and feature/bug `validation.md`.
- Agentic orchestrators `dev-feature-agent` and `dev-bug-agent`: decide after intake and stop before `dev-ship`.
- Manual steps end with the next skill.
- Ship-ready has one definition, the `dev-ship` preconditions: `validate_state.py`, the flow validator on `validation.md` with `--require-pass`, and `validate_readiness.py` (both reviews `APPROVE`, no `gap` or `not-checked` row, no tracked or untracked file outside `.dev/` since the reviewed commit). Agents run the same commands before the pre-ship stop. A bug directory without `validation.md` fails validation.
- `validate_design.py` checks that a Figma design has a visual contract citing the screen node-id, or declares `Visual design: INCOMPLETE`; the spec contract must cite the screen node-id. Row facts are judged by verify and QA, not by keyword.
- MR review emits `APPROVE` / `ADJUST` / `BLOCK` / `INCOMPLETE`.
- Figma design context marks hidden layers and masks (`maskType` included), keeps hidden paints and effects flagged in place, names components, variants, and styles, and passes rotation through without asserting a unit. A node id returns its subtree until `depth` or the node/byte cap; any cut sets `truncated` and says how to fetch the next level. Missing node ids are reported. A variables or screenshot failure stays a warning and keeps the nodes already fetched.
- MR review routes `INCOMPLETE` back to itself when the target, diff, or access is missing. `dev-fix-reviews` names that review when the round has no code gap, and stops after three such rounds.
- A bug debug with no demonstrable cause closes on `dev-debug`. A confirmed cause still closes on `dev-fix-bug`.
- Feature verify returns to `dev-execute` on the first and second FAIL. The third FAIL escalates with `Next skill: none`.
- Design and tasks are skipped only when the feature is small, normal risk, and has no screen. A screen, a large size, or high risk keeps `dev-design`, including when the spec adds that fact after an intake skip.
- A findings gate names every finding in the chat above the question card. The card title stays the one-line placeholder. Gate C does not open when there is no finding to name.
- Figma variables are optional. A 403 or a missing variables payload does not make design or QA `INCOMPLETE` and does not block dimension (b). Design context does not request variables unless `includeVariables` is true.
- Reviews keep their full report in chat. Inside a flow, each writes only its verdict, open-row count, and reviewed commit to `reviews/readiness.md`.
- Every validation verdict requires Completeness, and a missing verdict line fails. INCOMPLETE verification routes back to the verifier instead of to a fix.
- Agents reset `mode: manual` when they stop and close with a run log of autonomous decisions and artifacts. A stale `mode: agent` from an interrupted run does not apply to a skill the user invokes directly. Every blockage names its resume skill.
- Steps that write an artifact without a gate (execute, verify, fix-reviews) point to it in chat with a summary; verify repeats the Completeness table.

## 0.1.0 — 2026-09-02

- Two flows: Feature (spec-driven) and Bug (root-cause-first).
- `dev-*` skills bound to the `dev.mcp` server.
- Canonical `dev-qa-guided-review` and `dev-mr-guided-review`.
- Deterministic validators, contract fixtures, and CI without secrets.
- MIT license.
