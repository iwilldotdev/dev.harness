# Design fidelity — pixel-perfect (Step 1.5 and dimension b)

Read at Step 1.5 (pointer resolution) and again at Step 2 track (b). Does not replace `mcp-allowlist.md`.

Failure contract: a ticket points at a spec sheet (`85:1999`, “SEE THIS SCREEN”); the real screen/modal are other nodes in the same file (`203:11374`, `203:13054`), linked by an internal hyperlink. The skill **must** list spec **and** screen at Gate B, compare the screen/component screenshot at Gate C, and **refuse** to close the GAP with a generic `Modal` whose copy is not in the frame.

## Spec-sheet vs screen/component

| Type | Signals | Useful for |
|---|---|---|
| **Spec-sheet** | Requirements text, “see this screen”, micro-interaction sheet, annotations, little product layout | Dimension (a) and the **state** list (hover/open/empty/disabled). Does **not** replace (b). |
| **Screen / component** | Artboard with UI, page/screen name, visible modal/drawer/empty, overlay, CTA, background assets | The **only** target of dimension (b). |

If only a spec-sheet remains in inventory after Step 1.5, (b) = `INCOMPLETE` or GAP “target frame unresolved”. Do **not** degrade to “analyze the spec only”.

## Step 1.5 — Resolve pointers (required)

The parser (`extract_refs.py`) only sees URLs with `node-id` in the query, `node-id=` in text, `id="N:M"` in XML, and bare IDs `N:MMM` (`figma_node_ids`). Figma internal hyperlinks **do not** appear there. After `figma_get_design_context` / `figma_get_metadata` on the node extracted from the ticket/MR:

1. Run metadata XML/text + node copy through `extract_refs.py` (`figma_node_ids`).
2. Treat as a pointer if copy contains: “see this screen”, “this screen”, “see frame”, “see the modal”, “visual reference”.
3. Extract destinations from: hyperlinks, reactions, prototype connections, `prototypeNodeId`, `related` nodes, IDs in text.
4. **One hop** required: fetch each destination with `figma_get_metadata` + `figma_get_design_context` (`nodeIds`, screenshot + variables). Do not scan the file.
5. In the **same page section**, include visible siblings of the cited component (modal, drawer, empty, hover) — no second hop outside the section.
6. Classify each node: `spec` or `screen`. Each `screen` enters the Gate B inventory as extra `fileKey` + `node-id`.
7. A pointer that **does not resolve** → (b) incomplete. Do not continue (b) with the spec-sheet alone.
8. `figma_get_comments` only if the AC cites a comment.

Quota: do not call `figma_get_file` without `depth`/`ids`. One hop + section siblings is the cap, unless the user points at another `node-id`.

## Dimension (b) target: pixel-perfect

Target = visual parity with the **screen/component** frame, not “there is a Modal”.

Minimum method **per UI surface in the diff** (and per spec-cited state: hover/open/empty/disabled):

1. Screenshot of the **screen/component node** (`figma_get_screenshot` or URL in `figma_get_design_context`).
2. Read the component in the working tree: project Tailwind classes, tokens, literal copy, hierarchy, CTA, overlay, assets.
3. Reportable mismatch checklist: position, size, radius, overlay, typography (the project’s **custom** scale — token/config docs if they exist; do not assume a default scale), literal copy, hierarchy, CTA, background asset.

Rules:

- “Approximately the design system” is **not** OK.
- A spec-sheet screenshot does **not** count as (b) evidence.
- (b) `OK` only if every visible diff surface has a compared **screen** frame (Gate C must confirm those `node-id`s).
- No pixel-diff engine in this version. An app browser is optional; Figma × code is required.
- Figma variables 403 / quota / cropped frame → declare **unknown** in section 8; do **not** mark (b) OK.
- Do not claim visual fidelity without a screen-frame screenshot. Conversely: **do not close a visual GAP without that frame**.

## Visual GAP follow-up (skill stays read-only)

The report and any implementation follow-up inherit this:

- A (b) GAP does **not** close with a generic DS component (`Modal`/`Drawer`), copy from another i18n key, or an “equivalent flow”.
- The next agent **must** open the **screen** `node-id` (not only the spec) **before** writing UI.
- Marketing/onboarding frame (e.g. a wide modal with preview): implement **that** layout, or ask product. Do not invent a CTA that is not in the frame.

If the proposed fix is a `Modal` whose copy/layout is not in the screen screenshot, the GAP **did not close**.
