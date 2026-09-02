# dev.harness

Agent skills for a gated development cycle on top of [dev.mcp](https://github.com/iwilldotdev/dev.mcp). The server exposes Figma, Jira, Confluence, and GitLab tools; this repo is the workflow — gates, evidence, and steps. Without a ready `dev.mcp` server, skills stop at Step 0. The server alone does not enforce that workflow.

## Two flows

`dev-cycle` only routes. Invoke `dev-feature-cycle` or `dev-bug-cycle` directly when the type is already clear.

**Feature (spec-driven)** — what new behavior must exist, why, and how to prove it was delivered:

`dev-feature-intake` → `dev-specify` → (`dev-design` / `dev-tasks` when large or high-risk) → `dev-execute` → `dev-verify-feature` → dual review → `dev-ship`

**Bug (root-cause-first)** — why observed diverges from expected, and the smallest proven fix of the cause:

`dev-bug-intake` → `dev-reproduce-bug` → `dev-debug` → `dev-fix-bug` → `dev-verify-bug` → dual review → `dev-ship`

Bugs do **not** go through spec/design/tasks. Features do **not** treat `dev-debug` as a default step (only if a task fails). Independent verification (`author ≠ verifier`) and evidence-or-zero apply to both.

## Quick start

1. Clone next to [dev.mcp](https://github.com/iwilldotdev/dev.mcp).
2. Configure the server in your MCP host (`env` holds tokens — never this repo). See the server README for client configs.
3. Follow [INSTALL.md](INSTALL.md) to link `dev-*` skills into the host skill path.
4. Confirm a ready MCP server named `dev.mcp` (hosts may prefix the name).
5. For shared use, pin a SemVer tag; `main` may change gates and artifacts.

Python 3 is the only skill runtime. No installer daemon.

## Skills `dev-*`

| Skill | Role |
| --- | --- |
| `dev-shared` | MCP bind, gates, allowlists, parser, state |
| `dev-cycle` | Feature × Bug router |
| `dev-feature-cycle` | Feature orchestrator |
| `dev-feature-intake` | Target, Jira/Figma/GitLab, risk |
| `dev-specify` | Traceable requirements |
| `dev-design` | Technical surface + spec vs screen inventory |
| `dev-tasks` | Atomic tasks |
| `dev-execute` | Local implementation against spec/screen |
| `dev-verify-feature` | Fresh feature verifier |
| `dev-bug-cycle` | Bug orchestrator |
| `dev-bug-intake` | Symptom, severity, target |
| `dev-reproduce-bug` | Required reproduction |
| `dev-debug` | Root cause (read-only) |
| `dev-fix-bug` | RED test + minimal patch |
| `dev-verify-bug` | Fresh bug verifier |
| `dev-mr-guided-review` | Code review (read-only) |
| `dev-qa-guided-review` | QA AC × Figma × integration (read-only) |
| `dev-fix-reviews` | Closes confirmed gaps |
| `dev-ship` | MR / Jira after Gate S |

## Artifacts in the target project

Git-native memory under `.dev/features/<slug>/` (feature) and `.dev/bugs/<slug>/` (bug). Dual-review reports stay **in chat**; `reviews/round-NNN.md` stores only confirmed findings.

## Permissions

- Intakes, planning, reproduce, debug, verify, and reviews: absolute MCP write denylist.
- `dev-execute` / `dev-fix-bug` / `dev-fix-reviews`: working tree + local commits.
- `dev-ship`: `gitlab_save_merge_request` and, if Gate S authorizes, Jira comment/transition/link. Never accept an MR or force-push.

See [docs/architecture.md](docs/architecture.md), [INSTALL.md](INSTALL.md), [AGENTS.md](AGENTS.md).

## License

[MIT](LICENSE)
