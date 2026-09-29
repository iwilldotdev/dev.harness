---
name: dev-cycle
description: >-
  Router that classifies a request as Feature or Bug via dev.mcp, confirms
  ambiguous cases at Gate 0, and delegates to dev-feature-cycle or
  dev-bug-cycle. Does not plan, diagnose, or implement. Use as the default
  entry when the flow type is unknown.
compatibility: python3, dev.mcp
---

# Cycle (router)

Load [../dev-shared/SKILL.md](../dev-shared/SKILL.md). Does **not** plan, diagnose, implement, write code, or open an MR.

## Steps (this only)

1. Bind `dev.mcp` (hosts may prefix the name) and require ready. Failed → stop.
2. Extract the minimum: `extract_refs.py` on the user text; smoke `gitlab_whoami` if resolving a target. No broad fetch.
3. Classify:
   - **Feature** — creates or expands behavior.
   - **Bug** — corrects expected vs actual.
   - Refactor with no behavior change, investigation, incident without a requested fix, or a “Bug” ticket whose request adds product → evidence in chat and **Gate 0**.
4. A Jira ticket is a signal, not absolute truth.

## ⛔ Gate 0

Only when the class is ambiguous. Inventory and evidence **in chat**, as a Gate briefing (confirming, artifact `none`, summary, confirm vs reject). Question prompt verbatim: `Gate 0 — Confirm flow`. Short labels (`feature`, `bug`). `allow_multiple: false`. Do not re-ask a fact already obvious from the user text.

Invoking `dev-feature-cycle` or `dev-bug-cycle` **directly** skips this gate. Agentic modes are not a Gate 0 outcome: the user invokes `dev-feature-agent` or `dev-bug-agent` directly.

## Delegate

- Feature → load [../dev-feature-cycle/SKILL.md](../dev-feature-cycle/SKILL.md) and **end** this skill.
- Bug → load [../dev-bug-cycle/SKILL.md](../dev-bug-cycle/SKILL.md) and **end** this skill.

Do not inherit write tools. Do not run specify/execute/debug here.

The router only “finishes” a session when the delegated cycle ends **and** `validate_state.py` passes on the target project’s `.dev/STATE.md`.

## Close

Manual: the last line of the chat message is `Next skill: \`dev-feature-cycle\`` when the class is feature, or `Next skill: \`dev-bug-cycle\`` when the class is bug.
