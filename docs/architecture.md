# Architecture

```
request → dev-cycle (router)
            ├─ Feature → dev-feature-cycle
            │    intake → specify → [design] → [tasks] → execute → verify-feature
            │    → mr-guided-review → qa-guided-review → [fix-reviews] → ship
            └─ Bug → dev-bug-cycle
                 intake → reproduce → debug → fix-bug → verify-bug
                 → mr-guided-review → qa-guided-review → [fix-reviews] → ship
```

`dev-cycle` does not do heavy work. Each orchestrator loads only the current skill. The main session owns gates, hyperlinks, and state. Fresh workers own execute/verify.

Artifacts live in the **target project**, not this repo:

- `.dev/STATE.md` — flow, last gate, branch, next step
- `.dev/features/<slug>/` — intake, spec, design, tasks, validation, `reviews/round-NNN.md`
- `.dev/bugs/<slug>/` — intake, reproduction, investigation, hypothesis, fix-plan, validation, optional postmortem

Canonical reviews stay in chat. `round-NNN.md` only after confirmation.

## Gates

Inventory in chat. The question prompt is a one-line placeholder. If the host has a structured question tool, use it (`allow_multiple: false`); otherwise numbered labels after the inventory.

| id | prompt |
| --- | --- |
| `gate-flow` | `Gate 0 — Confirm flow` |
| `gate-feature-context` | `Gate F-A — Confirm context` |
| `gate-feature-spec` | `Gate F-B — Confirm requirements` |
| `gate-feature-design` | `Gate F-C — Confirm design` |
| `gate-feature-tasks` | `Gate F-D — Confirm execution` |
| `gate-feature-debug` | `Gate F-X — Confirm task diagnosis` |
| `gate-bug-context` | `Gate B-A — Confirm symptom and severity` |
| `gate-bug-reproduction` | `Gate B-B — Confirm reproduction` |
| `gate-bug-hypothesis` | `Gate B-C — Confirm root cause` |
| `gate-bug-fix` | `Gate B-D — Confirm minimal patch` |
| `gate-ship` | `Gate S — Confirm remote actions` |

QA keeps its own Gates A/B/C.

## Permissions

No-escalation: the current skill does not inherit the next skill’s writes.

- Read-only MCP: router, orchestrators, intakes, specify/design/tasks, reproduce, debug, verify, reviews.
- Working tree: `dev-execute`, `dev-fix-bug`, `dev-fix-reviews`.
- Remote: only `dev-ship` after Gate S (`gitlab_save_merge_request`; Jira if selected).
