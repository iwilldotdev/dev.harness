# Ship preflight

Before Gate S, in the **target project**:

1. `git status` / `git branch --show-current` — working tree clean enough for the MR; unrelated changes preserved.
2. Remote `origin` → `projectId` via `extract_refs.py` (same Gate A contract).
3. Merge-base with the target (MR default or confirmed base branch). Ambiguous base → `Gate A — Confirm merge-base`.
4. Diff range `git diff <merge-base>...<HEAD>` + commit list. Do not invent an IID if there is no MR.
5. Conflicts: `git merge-tree` or a conceptual dry rebase; if risky, stop and ask for consent. Never `reset --hard`.
6. Receipts: SHA, range, command, result. No tokens or full logs.
