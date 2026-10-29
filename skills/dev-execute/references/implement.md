# Implementation

- Tests come from the spec, not from the code.
- The gate is the test runner, not self-assessment.
- One commit per task; include traceability updates in the same commit.
- Local blast radius. Push only via `dev-ship`.
- Conventional Commits; no `Co-authored-by` / host attribution trailers.
- If the environment cannot run the relevant runtime, declare INCOMPLETE — do not infer from the code.
- UI receipt is a table per screen region (`região | node-id | fato | valor aplicado`): fixed size, absolute position, complex fill, effect, stroke, opacity, and literal copy. The values come from the Figma pack (`figma/<node-id>.json`), refetched only when `figma_get_file_meta` shows a newer `lastModified`. A generic component does not replace a `FIXED` or `ABSOLUTE` node.
