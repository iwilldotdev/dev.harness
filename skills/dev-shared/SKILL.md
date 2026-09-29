---
name: dev-shared
description: >-
  Shared primitives for the dev.harness: bind only the dev.mcp server,
  gates with a briefing in chat, evidence-or-zero, allowlists, extract_refs.py,
  git safety, and .dev/STATE.md. Load when any other dev-* skill starts. Do
  not use as a standalone workflow.
disable-model-invocation: true
compatibility: python3, dev.mcp
---

# Shared primitives

`SKILL_DIR` = the folder that contains this `SKILL.md`. Resolve it at runtime.

Before any `dev-*` step, read in full:

1. [references/mcp-bind.md](references/mcp-bind.md)
2. [references/gates.md](references/gates.md)
3. [references/allowlists.md](references/allowlists.md)
4. [references/evidence-contract.md](references/evidence-contract.md)
5. [references/phase-grounding.md](references/phase-grounding.md)
6. [references/risk-classification.md](references/risk-classification.md)
7. [references/extract-refs.md](references/extract-refs.md)

Agent mode is active only when `.dev/STATE.md` has `mode: agent` **and** `dev-feature-agent` or `dev-bug-agent` loaded this skill in the current conversation. Then read [references/agent-mode.md](references/agent-mode.md) in full before any gate. A skill the user invoked directly runs in manual mode even if `STATE.md` still says `mode: agent` (an interrupted run): write `mode: manual` first. Every `mode: agent` rule in a step skill means this active agent mode.

Parser: `python3 "$SKILL_DIR/scripts/extract_refs.py"` (no network). State: `python3 "$SKILL_DIR/scripts/validate_state.py"`. Commits: `python3 "$SKILL_DIR/scripts/check_commit.py"`.

This skill does **not** implement a feature or a bug. It only defines the contract other skills must follow.
