# Gates — chat then ask

At **every** checkpoint:

1. Write the body in **chat** (Markdown). Clickable URLs. Inventory, IDs, risks, and evidence stay **here**.
2. Then ask the user. If the host has a structured question tool, use it (`allow_multiple: false`). The `prompt` is **only** the one-line placeholder. Labels are short. Otherwise list numbered labels after the inventory already in chat.
3. Do not copy inventory, hyperlinks, `fileKey`, `node-id`, or Jira keys into the prompt or labels.
4. A negative answer returns to the phase that produced the artifact. Update `.dev/STATE.md` only **after** the answer.

Placeholders verbatim:

| id | prompt |
| --- | --- |
| `gate-flow` | `Gate 0 — Confirm flow` |
| `gate-a-target` | `Gate A — Confirm target` |
| `gate-a-base` | `Gate A — Confirm merge-base` |
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

QA (`dev-qa-guided-review`) keeps its own Gates A/B/C (`Gate B — Enough context?`, `Gate C — Confirm findings?`).
