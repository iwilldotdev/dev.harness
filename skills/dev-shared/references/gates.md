# Gates — chat then ask

At **every** checkpoint in **manual** mode (`mode` absent or `mode: manual`), except the intake gap round:

1. Write the **Gate briefing** as the visible chat prose **above** the question card, in the same turn, **before** calling the question tool. The card does not show the briefing. Clickable URLs. Inventory, IDs, risks, and evidence stay **here**. Exploration, a file name, or “Asking questions” is not a briefing. Do not open the question until that prose is in the message.
2. Then ask **one** question. If the host has a structured question tool, use it (`allow_multiple: false`). The `prompt` is **only** the one-line placeholder. Labels are short. Otherwise list numbered labels after the briefing already in chat.
3. Do not copy inventory, hyperlinks, `fileKey`, `node-id`, or Jira keys into the prompt or labels.
4. Do not re-ask a fact already recorded under `## Decisions` in the intake.
5. A negative answer returns to the phase that produced the artifact. Update `.dev/STATE.md` only **after** the answer.

## Gate briefing

Required in chat before the question. Omit nothing because the file exists on disk.

- **Confirming:** what this gate decides
- **Artifact:** repo path (`.dev/features/<slug>/…` or `.dev/bugs/<slug>/…`), or `none` when this gate has no file yet
- **Summary:** a few lines of what that artifact or the evidence actually says. “See the file” is not a summary. A findings gate names every finding in one line (what was checked, the evidence, and what confirming it authorizes). A card titled only “Confirm findings?” with no finding named above it is not a briefing.
- **Confirm:** what a positive answer authorizes, and which skill that leads to
- **Reject:** which skill a negative answer returns to

## Intake gap round

The one question round inside `dev-feature-intake` / `dev-bug-intake`, in both modes. Use it only when at least one fact is unresolved after reading the ticket, Figma, git, and code.

1. Gate briefing in chat: what is already known (with links), then one short line per open gap.
2. This form is the exception to the one-question rule above. One structured form with id `gate-intake-gaps` holds every gap: each gap is its own question with `allow_multiple: false`. The question prompt is a one-line label (`Target MR`, `Merge-base`, `Acceptance criterion`, `Screen frame`, `Expected vs actual`, `Severity`). Options are the real candidates found; always include a free-text path for the user’s own answer. Do not collapse the gaps into a single choice. Without a structured tool: numbered questions in one message.
3. An ambiguous target is answered here with `Target MR` / `Merge-base` questions. Do not ask `Gate A — Confirm target` as a separate round.
4. Record every answer under `## Decisions` in `intake.md`. Then continue to the intake gate (manual) or decide it (agent).

No inventory, URL, `fileKey`, `node-id`, or Jira key in prompts or labels; those stay in the briefing.

## Agent mode

Agent mode is active only when `.dev/STATE.md` has `mode: agent` **and** an agent orchestrator loaded the current skill in this conversation. A skill the user invoked directly asks its gates and writes `mode: manual` first. In active agent mode, do **not** ask. Read [agent-mode.md](agent-mode.md) and follow it. The intake gap round is the only question, and it happens inside intake. **Exception:** `dev-ship` Gate S always asks, even when `mode` is `agent`.

## Closing line (manual)

When a manual step wrote or updated an artifact, gate or not (`spec.md`, `validation.md`, `reviews/round-NNN.md`, commits), the closing message names each path, or SHA, with a few lines of what it says. A verdict artifact repeats its `## Completeness` table in chat. “See the file” is not a summary.

When a manual step finishes, the last line of the chat text is:

`Next skill: \`dev-...\``

If the successor depends on a condition, that same line states the condition. `dev-ship` ends the cycle: `Next skill: none`.

In agent mode, do not emit this line between steps. The orchestrator loads the next skill. Only a stop emits it: `Next skill: \`dev-ship\`` at the pre-ship stop, or the manual resume skill on a blockage. Every stop first writes `mode: manual`.

Placeholders verbatim:

| id | prompt |
| --- | --- |
| `gate-flow` | `Gate 0 — Confirm flow` |
| `gate-intake-gaps` | `Intake — Resolve gaps` (form title; one labeled question per gap) |
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

QA (`dev-qa-guided-review`) keeps its own Gates A/B/C (`Gate B — Enough context?`, `Gate C — Confirm findings?`). The Gate briefing still applies.
