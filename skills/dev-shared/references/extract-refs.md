# Parser `extract_refs.py`

No network. Input: `--text`, `--file`, or stdin. JSON output: `jira_keys`, `figma`, `figma_node_ids`, `gitlab.mrs`, `gitlab.project_paths`.

```bash
python3 "$SKILL_DIR/scripts/extract_refs.py" --text "PROJ-123 https://gitlab.example.com/g/app/-/merge_requests/42"
python3 "$SKILL_DIR/scripts/extract_refs.py" --self-test
```

GitLab `projectId` = path from the remote (`git remote get-url origin` → parser), never the local clone path.

The parser does **not** resolve Figma internal hyperlinks. That is Step 1.5 in `design-fidelity.md`.

`dev-qa-guided-review/scripts/extract_refs.py` is a thin wrapper around this file. Do not diverge the logic.
