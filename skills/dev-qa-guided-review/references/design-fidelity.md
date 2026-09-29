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

1. Screenshot of the **screen/component node** (`figma_get_screenshot` or URL in `figma_get_design_context`) for the overall picture.
2. Numbers come from that node’s `nodes[]` (`visual`, `layout`, `fills`, `strokes`, `text`), not from the screenshot alone.
3. Read the component in the working tree: project Tailwind classes, tokens, literal copy, hierarchy, CTA, overlay, assets.
4. Reportable mismatch checklist: position, size, radius, overlay, typography (the project’s **custom** scale — token/config docs if they exist; do not assume a default scale), literal copy, hierarchy, CTA, background asset, plus the visual-contract types below.

Rules:

- “Approximately the design system” is **not** OK.
- A spec-sheet screenshot does **not** count as (b) evidence.
- (b) `OK` only if every visible diff surface has a compared **screen** frame (Gate C must confirm those `node-id`s).
- No pixel-diff engine in this version. An app browser is optional; Figma × code is required.
- Figma variables 403 / quota / cropped frame, a `warnings` entry, or a design-context payload with `truncated` / `childrenTruncated` → declare **unknown** in the report’s Unknowns section; do **not** mark (b) OK. `truncation.hint` says to pass `depth` or a child `node-id`. A node with `childrenTruncated` can be fetched on its own `node-id` to close that unknown. A `warnings` entry means the nodes that did return are still usable, and the failed part stays unknown.
- Do not claim visual fidelity without a screen-frame screenshot. Conversely: **do not close a visual GAP without that frame**.

## Visual contract

Build one contract per **screen** node (and per cited state). Specify, design, execute, verify, and review all use this same list. A spec-sheet does not produce a visual contract.

| Fact | Where it lives | How to treat it |
| --- | --- | --- |
| Visibility / mask | node `visible: false`, `isMask: true`, `maskType` (`ALPHA`, `VECTOR`, `LUMINANCE`); `visible: false` inside a paint of `fills` / `strokes` or an effect of `visual.effects` | A hidden node and its whole subtree are not rendered; a hidden paint or effect is not rendered either. Do not implement them. A mask clips the siblings above it; it is not visible content. `ALPHA` clips by alpha, `VECTOR` by the vector outline, and `LUMINANCE` by luminance. Keep the operation; do not treat every mask as the same clip. |
| Component | `component` (name, key, `set`), `componentProperties`, `styleNames` | Use that design-system component with those variant values, and the named text/color style. A raw value that differs from its named style is a `token` mismatch. |
| Fixed size | `visual.sizing` `FIXED` plus `size` | Literal px, or the token when `visual.boundVariables` names one. Do not swap in a generic design-system size. `visual.rotation` is passed through as REST returns it; the REST docs do not state the unit, so confirm it against the screen screenshot before writing CSS (a quarter turn reads about `90` in degrees or about `1.57` in radians). With it set, `size` is the rotated bounding box, not the element’s own size: record the rotation and declare the intrinsic size unknown instead of copying the box. |
| Hug / fill | `visual.sizing` `HUG` or `FILL`; `layout.layoutGrow`, `layout.layoutAlign`, min/max, `layoutWrap`, axis sizing | Hug content or fill the parent, including a child that grows or stretches. Do not freeze a hug node at the screenshot’s pixel width. |
| Absolute position | `visual.positioning` `ABSOLUTE`, `position`, `visual.constraints` | Positioned overlay, not an auto-layout sibling. |
| Complex fill | `fills` (several paints, gradient stops, image) | Name each paint. Do not flatten to one solid token. |
| Effect | `visual.effects` | Keep the REST effect, including blend, shadow-behind, blur type, offset, spread, and color. Do not flatten the color to CSS. |
| Radius | `visual.radius` (one number or four corners) | Per-corner values stay per-corner. |
| Stroke | `visual.stroke` weight, align, individual sides; `strokes` | Align (inside / center / outside) is part of the size. |
| Opacity / blend | `visual.opacity`, `visual.blendMode` | A non-default blend is a complex style, not “slightly transparent”. |
| Text | `text` family, `fontStyle`/`italic`, size, weight, line height (`lineHeightPx`, or `lineHeightPercentFontSize` with `lineHeightUnit`), letter spacing, `align`, `decoration`, `case`, `characters`, `characterStyleOverrides`, `styleOverrideTable` | Literal copy, including mixed styles inside one text node. Do not borrow another i18n key. A `FONT_SIZE_%` line height stays relative to the font size; do not freeze it to px. |
| Text sizing | `text.autoResize`, `text.truncation`, `text.maxLines` | `NONE` is a fixed text box; `HEIGHT` grows vertically at fixed width; `WIDTH_AND_HEIGHT` hugs. `ENDING` truncates with an ellipsis after `maxLines`. |

Mismatch types that must be available in review: `layout`, `typography`, `overlay`, `asset`, `spacing`, `token`, `state`, `copy`, `missing`, `fixed-size`, `absolute`, `effect`, `complex-fill`, `stroke`, `opacity`.

Forbidden summary: “use a Modal/Drawer”, “close enough to the DS”, “equivalent flow”.

## Visual GAP follow-up (skill stays read-only)

The report and any implementation follow-up inherit this:

- A (b) GAP does **not** close with a generic DS component (`Modal`/`Drawer`), copy from another i18n key, or an “equivalent flow”.
- The next agent **must** open the **screen** `node-id` (not only the spec) **before** writing UI.
- Marketing/onboarding frame (e.g. a wide modal with preview): implement **that** layout, or ask product. Do not invent a CTA that is not in the frame.

If the proposed fix is a `Modal` whose copy/layout is not in the screen screenshot, the GAP **did not close**.
