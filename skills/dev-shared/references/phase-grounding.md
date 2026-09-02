# Phase grounding

Before producing an artifact, read **only** the code, docs, git, and MCP evidence relevant to that phase. Record sources. Do not load every spec and skill at once.

Order (never jump to “unknown” if 1–3 exist):

1. Codebase — patterns, tests, contracts already in the repo
2. `.dev/` artifacts for the current feature/bug + `STATE.md`
3. `dev.mcp` — Jira/Figma/GitLab allowlisted for the phase
4. Explicit uncertainty — never invent an API, AC, or cause

Feature: read-only code grounding at intake; design focuses on interfaces/callers. Bug: change analysis (`git log`, pipelines, commit) before a hypothesis.

Fresh agent context for heavy execute/verify. Effort matches risk. Feature batches ~5–7 tasks per worker; a bug uses a separate fixer and verifier.
