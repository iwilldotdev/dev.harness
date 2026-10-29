# Parser `extract_refs.py`

No network. Input: `--text`, `--file`, or stdin. JSON output: `jira_keys`, `figma`, `figma_node_ids`, `figma_pointers`, `gitlab.mrs`, `gitlab.project_paths`.

```bash
python3 "$SKILL_DIR/scripts/extract_refs.py" --text "PROJ-123 https://gitlab.example.com/g/app/-/merge_requests/42"
python3 "$SKILL_DIR/scripts/extract_refs.py" --self-test
```

GitLab `projectId` = path from the remote (`git remote get-url origin` → parser), never the local clone path.

`figma_node_ids` covers URLs with `node-id`, `node-id=` in text, `id="N:M"` in XML, bare IDs `N:MMM`, and pointer destinations. `figma_pointers` covers **only** the pointer destinations read from a REST payload or metadata XML: `prototypeNodeId`, `destinationNodeId` (prototype reactions), and `nodeId` inside a `hyperlink` object, plus the XML attrs `prototypeNode` / `hyperlinkNode` that `figma_get_metadata` emits when they exist. These are the destinations of Figma internal links — the design-fidelity "one hop" — and they no longer depend on prose: `figma_get_design_context` passes `hyperlink` and `reactions` through on every node.

`dev-qa-guided-review/scripts/extract_refs.py` is a thin wrapper around this file. Do not diverge the logic.
