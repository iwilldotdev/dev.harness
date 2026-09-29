# Agent mode

Set by `dev-feature-agent` or `dev-bug-agent` as `.dev/STATE.md` `mode: agent`. Manual cycles leave `mode` unset, and a manual cycle invoked on a `mode: agent` state sets `mode: manual` before its first step (`dev-ship` Gate S asks either way).

`mode: agent` lives only while the agent runs. Every stop (blockage or pre-ship) writes `mode: manual` before the closing message, so the skill the user runs next asks its gate and ends with `Next skill:`. Invoking the agent again sets `mode: agent` again.

A run can also end without a stop (cancelled, out of context). The value then left in `STATE.md` does not count: agent mode applies only to a skill the orchestrator loaded in the current conversation. A skill the user invokes directly writes `mode: manual` and runs its manual gates.

Before any stop, run `validate_state.py` on `.dev/STATE.md`. A non-zero result is part of the blockage. Before the pre-ship stop, also run the other `dev-ship` precondition commands. Do not call a stop ship-ready while any of them fails.

## Questions

The only question is the intake gap round. After `## Decisions` is written, do not ask again. Do not open a later gate prompt.

## Decisions

At each later gate:

1. Read `## Decisions`, the current artifact, and the surrounding evidence (ticket, Figma **screen**, git, code, prior artifacts).
2. When that is enough to proceed without inventing an acceptance criterion, copy, root cause, screen, or target, record `decision: proceed` and one sentence of evidence in the artifact. Set `gate:` in `STATE.md`. Chat-only reviews record the decision in chat + `STATE.md`. The orchestrator then loads the next skill.
3. Do not invent. When the surroundings still cannot support the next step, stop. Write `mode: manual`, then the run log (below). Explain the blockage in chat (what is missing, what was already checked). The last line is `Next skill: \`dev-...\`` with the manual skill that resumes. Do not open another question round.

Blockages that stop the agent:

| Blockage | Resume skill |
| --- | --- |
| Bug `NOT REPRODUCED` and no CI job anchor | `dev-reproduce-bug` |
| Screen frame still unresolved after the intake round | the intake skill of the flow |
| No demonstrable cause | `dev-debug` |
| Third failed fix attempt | `dev-debug` |
| Verification `INCOMPLETE` (no runtime, surface, or access) | `dev-verify-feature` / `dev-verify-bug` |
| Review `INCOMPLETE` for a missing screen, target, or access | that review skill |
| Product behavior that is not in the ticket, the intake decisions, or the screen frame | `dev-feature-cycle` |
| A `dev-ship` precondition command fails after the review loop | the skill that owns the failing artifact |

A single opened MR, a clear branch mode, a classified small+normal skip, or a visual fact present on the screen node is a decision, not a question.

## What still runs

Verify, both reviews, and `dev-fix-reviews` stay on the path. In agent mode, findings the agent just wrote with evidence are the confirmed gaps: record the round and continue the return skill. Do not skip verify. Max three review rounds, then stop and explain.

High-risk does not add a question. It keeps full rigor and stays marked for the human at the pre-ship stop.

## Ship

Ship-ready means every command in the [`dev-ship` preconditions](../../dev-ship/SKILL.md#preconditions) exits 0: `validate_state.py`, the flow validator on `validation.md` with `--require-pass`, and `validate_readiness.py`. Anything else loops through `dev-fix-reviews` or stops as a blockage.

Do not load `dev-ship`. Write `mode: manual`. Stop with the run log, then the Gate S briefing (diff range, commits, target branch, Jira, MR title/body, exact remote actions, risk). The last line is `Next skill: \`dev-ship\``.

When the user invokes `dev-ship`, Gate S stays manual even if `mode` is still `agent`.

## Run log

Every stop opens with this log in chat. The pre-ship stop is the only human review of the run, so every decision taken without asking is visible here.

| Step | Artifact | Decision | Evidence |
| --- | --- | --- | --- |
| skill that ran | repo path, or `chat` | `proceed`, skip, N/A dimension, return skill | one sentence |

After the table:

- Intake `## Decisions`, as answered in the gap round
- Loops: execute↔verify and review rounds, with the reason for each return
- Latest Completeness of `validation.md`, MR review, and QA (rows and verdicts)
- High-risk items the human must weigh at Gate S
