# Architecture

```
request → dev-cycle (router)
            ├─ Feature → dev-feature-cycle
            │    intake (gap round) → specify → [design] → [tasks] → execute → verify-feature
            │    → mr-guided-review → qa-guided-review → [fix-reviews] → ship
            └─ Bug → dev-bug-cycle
                 intake (gap round) → reproduce → debug → fix-bug → verify-bug
                 → mr-guided-review → qa-guided-review → [fix-reviews] → ship

direct  → dev-feature-agent | dev-bug-agent
            same steps, decisions instead of gates, stop before ship
```

`dev-cycle` does not do heavy work and does not enter agent mode. Each orchestrator loads only the current skill. The main session owns gates, hyperlinks, and state. Fresh workers own execute/verify.

Artifacts live in the **target project**, not this repo:

- `.dev/STATE.md` — flow, mode (`manual` when absent), last gate, branch, next step
- `.dev/features/<slug>/` — intake (`## Decisions`, visual contract notes), spec, design, tasks, validation, `reviews/round-NNN.md`, `reviews/readiness.md`
- `.dev/bugs/<slug>/` — intake, reproduction, investigation, hypothesis, fix-plan, validation, `reviews/`, optional postmortem

Canonical reviews stay in chat and include a Completeness profile. `round-NNN.md` only after confirmation (manual) or after the agent recorded the evidence (agent mode). Inside a flow, each review also rewrites its verdict, open-row count, and reviewed commit in `readiness.md`; `dev-ship` refuses a receipt that is not approved or is older than the code.

## Gates

Manual mode: Gate briefing in chat (confirming, artifact path, summary, confirm vs reject), then the one-line question prompt. If the host has a structured question tool, use it (`allow_multiple: false`); otherwise numbered labels after the briefing. A finished manual step ends with `Next skill: \`dev-...\``.

Agent mode: one intake gap round, then decide from `## Decisions` and surrounding evidence. Stop before `dev-ship`. Gate S stays manual.

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

QA keeps its own Gates A/B/C. The Gate briefing still applies.

UI work uses the visual contract in `dev-qa-guided-review` (`visual.sizing` FIXED, absolute position, complex fills, effects, stroke, opacity, text). A spec-sheet is not a screen.

## Permissions

No-escalation: the current skill does not inherit the next skill’s writes.

- Read-only MCP: router, orchestrators, intakes, specify/design/tasks, reproduce, debug, verify, reviews.
- Working tree: `dev-execute`, `dev-fix-bug`, `dev-fix-reviews`.
- Remote: only `dev-ship` after Gate S (`gitlab_save_merge_request`; Jira if selected).
